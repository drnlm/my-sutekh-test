# CardSetListModel.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""The gtk.TreeModel for the card lists."""

from sutekh.core.Filters import FilterAndBox, NullFilter, SpecificCardFilter, \
        PhysicalCardSetFilter, SpecificCardIdFilter, \
        MultiPhysicalCardSetMapFilter, SpecificPhysCardIdFilter
from sutekh.core.SutekhObjects import PhysicalCard, IExpansion, \
        MapPhysicalCardToPhysicalCardSet, IAbstractCard, IPhysicalCard, \
        IPhysicalCardSet, PhysicalCardSet
from sutekh.gui.CardListModel import CardListModel, norm_path

# pylint: disable-msg=C0103
# We break out usual convention here
# consts for the different modes we need
NO_SECOND_LEVEL, SHOW_EXPANSIONS, SHOW_CARD_SETS, EXPANSIONS_AND_CARD_SETS, \
        CARD_SETS_AND_EXPANSIONS = range(5)
# Different card count modes
THIS_SET_ONLY, ALL_CARDS, PARENT_CARDS, CHILD_CARDS = range(4)
# Different Parent card count modes
IGNORE_PARENT, PARENT_COUNT, MINUS_THIS_SET, MINUS_SETS_IN_USE = range(4)
# pylint: enable-msg=C0103

class CardSetModelRow(object):
    """Object which holds the data needed for a card set row."""
    # This is intended to replace the overly complicated dictionary,
    # FIXME: Needs more work

    def __init__(self, bEditable, iExtraLevelsMode):
        self.dExpansions = {}
        self.dChildCardSets = {}
        self.dParentExpansions = {}
        self.iCount = 0
        self.iParentCount = 0
        self.iExtraLevelsMode = iExtraLevelsMode
        self.bEditable = bEditable

    def get_parent_count(self):
        """Get the parent count"""
        return self.iParentCount

    def get_inc_dec_flags(self, iCnt):
        """Deermine the status of the button flags."""
        if self.bEditable:
            return True, (iCnt > 0)
        return False, False

    def get_card_count(self):
        """Extract a card count from the grouped iterator"""
        return self.iCount

    def get_expansion_info(self):
        """Get information about expansions"""
        dCardExpansions = {}
        if self.iExtraLevelsMode in [SHOW_EXPANSIONS,
                EXPANSIONS_AND_CARD_SETS]:
            for sExpName, iCnt in self.dExpansions.iteritems():
                bIncCard, bDecCard = self.get_inc_dec_flags(iCnt)
                iParCnt = self.dParentExpansions.get(sExpName, 0)
                dCardExpansions[sExpName] = [iCnt, iParCnt, bIncCard, bDecCard]
        else:
            for sChildSet in self.dChildCardSets:
                dCardExpansions[sChildSet] = {}
                if not self.dExpansions.has_key(sChildSet):
                    continue
                for sExpName, iCnt in self.dExpansions[sChildSet].iteritems():
                    bIncCard, bDecCard = self.get_inc_dec_flags(iCnt)
                    iParCnt = self.dParentExpansions.get(sExpName, 0)
                    dCardExpansions[sChildSet][sExpName] = [iCnt, iParCnt,
                            bIncCard, bDecCard]
        return dCardExpansions

    def get_child_info(self):
        """Get information about child card sets"""
        dChildren = {}
        if self.iExtraLevelsMode in [SHOW_CARD_SETS, CARD_SETS_AND_EXPANSIONS]:
            for sCardSet, iCnt in self.dChildCardSets.iteritems():
                bIncCard, bDecCard = self.get_inc_dec_flags(iCnt)
                dChildren[sCardSet] = [iCnt, self.iParentCount, bIncCard,
                        bDecCard]
        else:
            for sExpName in self.dExpansions:
                iParCnt = self.dParentExpansions.get(sExpName, 0)
                dChildren[sExpName] = {}
                if not self.dChildCardSets.has_key(sExpName):
                    # No children for this expansion
                    continue
                for sCardSet, iCnt in \
                        self.dChildCardSets[sExpName].iteritems():
                    bIncCard, bDecCard = self.get_inc_dec_flags(iCnt)
                    dChildren[sExpName][sCardSet] = [iCnt, iParCnt, bIncCard,
                            bDecCard]
        return dChildren


def get_card(oItem):
    """Extract a absract card from the dictionary for groupby"""
    return oItem[0]

class CardSetCardListModel(CardListModel):
    # pylint: disable-msg=R0904, R0902
    # inherit a lot of public methods for gtk, need local attributes for state
    """CardList Model specific to lists of physical cards.

       Handles the constraint that the available number of cards
       is determined by the Physical Card Collection.
       """
    def __init__(self, sSetName):
        super(CardSetCardListModel, self).__init__()
        self._cCardClass = MapPhysicalCardToPhysicalCardSet
        self._oBaseFilter = PhysicalCardSetFilter(sSetName)
        self._oCardSet = IPhysicalCardSet(sSetName)
        self.iExtraLevelsMode = SHOW_EXPANSIONS
        self.bChildren = False
        self.iShowCardMode = THIS_SET_ONLY
        self.bEditable = False
        self._dNameSecondLevel2Iter = {}
        self._dName2nd3rdLevel2Iter = {}
        self.iParentCountMode = PARENT_COUNT
        self.sEditColour = None

    def format_count(self, iCnt):
        """Format the card count accorindly"""
        if self.bEditable and self.sEditColour:
            return '<i><span foreground="%s">%d</span></i>' % \
                    (self.sEditColour, iCnt)
        else:
            return '<i>%d</i>' % iCnt

    def format_parent_count(self, iCnt, iParCnt):
        """Format the parent card count"""
        if (self.iParentCountMode == PARENT_COUNT and iParCnt < iCnt) or \
                iParCnt < 0:
            return '<i><span foreground="red">%d</span></i>' % iParCnt
        else:
            return '<i>%d</i>' % iParCnt

    def load(self):
        # pylint: disable-msg=R0914
        # we use many local variables for clarity
        """
        Clear and reload the underlying store. For use after initialisation or when
        the filter or grouping changes.
        """
        self.clear()
        self._dName2Iter = {}
        self._dNameSecondLevel2Iter = {}
        self._dName2nd3rdLevel2Iter = {}
        self._dGroupName2Iter = {}

        oCardIter = self.get_card_iterator(self.get_current_filter())
        oGroupedIter, aAbsCards = self.grouped_card_iter(oCardIter)

        self.oEmptyIter = None

        # Iterate over groups
        for sGroup, oGroupIter in oGroupedIter:
            # Check for null group
            if sGroup is None:
                sGroup = '<< None >>'

            # Create Group Section
            oSectionIter = self.append(None)
            self._dGroupName2Iter[sGroup] = oSectionIter

            # Fill in Cards
            iGrpCnt = 0
            iParGrpCnt = 0
            for oCard, oRow in oGroupIter:
                iCnt = oRow.get_card_count()
                iParCnt = oRow.get_parent_count()
                iGrpCnt += iCnt
                iParGrpCnt += iParCnt
                oChildIter = self.append(oSectionIter)
                bIncCard, bDecCard = self.check_inc_dec_card(iCnt)
                self.set(oChildIter,
                    0, oCard.name,
                    1, self.format_count(iCnt),
                    2, self.format_parent_count(iCnt, iParCnt),
                    3, bIncCard,
                    4, bDecCard
                )
                self._dName2Iter.setdefault(oCard.name, []).append(oChildIter)

                self._add_children(oChildIter, oRow)

            # Update Group Section
            self.set(oSectionIter,
                0, sGroup,
                1, self.format_count(iGrpCnt),
                2, self.format_parent_count(iGrpCnt, iParGrpCnt),
                3, False,
                4, False
            )

        if not self._dName2Iter:
            # Showing nothing
            self.oEmptyIter = self.append(None)
            sText = self._get_empty_text()
            self.set(self.oEmptyIter, 0, sText, 1, self.format_count(0), 2,
                    '0', 3, False, 4, False)

        # Notify Listeners
        for oListener in self.dListeners:
            oListener.load(aAbsCards)

    def _add_children(self, oChildIter, oRow):
        """Add the needed children for a card in the model."""
        dExpansionInfo = oRow.get_expansion_info()
        dChildInfo = oRow.get_child_info()
        if self.iExtraLevelsMode == SHOW_EXPANSIONS:
            for sExpansion in sorted(dExpansionInfo):
                self._add_extra_level(oChildIter, sExpansion,
                        dExpansionInfo[sExpansion])
        elif self.iExtraLevelsMode == SHOW_CARD_SETS:
            for sChildSet in sorted(dChildInfo):
                self._add_extra_level(oChildIter, sChildSet,
                        dChildInfo[sChildSet])
        elif self.iExtraLevelsMode == EXPANSIONS_AND_CARD_SETS:
            for sExpansion in sorted(dExpansionInfo):
                oSubIter = self._add_extra_level(oChildIter,
                        sExpansion, dExpansionInfo[sExpansion])
                for sChildSet in sorted(dChildInfo[sExpansion]):
                    self._add_extra_level(oSubIter, sChildSet,
                            dChildInfo[sExpansion][sChildSet])
        elif self.iExtraLevelsMode == CARD_SETS_AND_EXPANSIONS:
            for sChildSet in sorted(dChildInfo):
                oSubIter = self._add_extra_level(oChildIter,
                        sChildSet, dChildInfo[sChildSet])
                for sExpansion in dExpansionInfo[sChildSet]:
                    self._add_extra_level(oSubIter, sExpansion,
                            dExpansionInfo[sChildSet][sExpansion])

    def check_inc_dec_card(self, iCnt):
        """Helper function to check whether card can be incremented"""
        if not self.bEditable:
            return False, False
        return True, (iCnt > 0)

    def _add_extra_level(self, oParIter, sName, tInfo):
        """Add an extra level iterator to the card list model."""
        oIter = self.append(oParIter)
        iCnt, iParCnt, bIncCard, bDecCard = tInfo
        self.set(oIter,
                0, sName,
                1, self.format_count(iCnt),
                2, self.format_parent_count(iCnt, iParCnt),
                3, bIncCard,
                4, bDecCard)
        # Add to the cache
        oPath = self.get_path(oIter)
        # get_card_name_from_path work's regardless of level
        sCardName = self.get_card_name_from_path(oPath)
        iDepth = self.iter_depth(oIter)
        if iDepth == 2:
            self._dNameSecondLevel2Iter.setdefault(sCardName, {})
            self._dNameSecondLevel2Iter[sCardName].setdefault(sName,
                    []).append(oIter)
        elif iDepth == 3:
            sSecondLevelName = self.get_name_from_iter(oParIter)
            tKey = (sCardName, sSecondLevelName)
            self._dName2nd3rdLevel2Iter.setdefault(tKey, {})
            self._dName2nd3rdLevel2Iter[tKey].setdefault(sName,
                    []).append(oIter)
        return oIter

    def check_inc_dec_expansion(self, iCnt):
        """Helper function to check status of expansions"""
        if not self.bEditable:
            return False, False
        return True, (iCnt > 0)

    def check_expansion_iter_stays(self, oCard, sExpansion, iCnt):
        """Check if the expansion entry should remain in the table"""
        # pylint: disable-msg=E1101
        # SQLObject confuses pylint
        if iCnt > 0:
            return True
        if self.bEditable:
            # Only stays visible if cards in the PhysicalCardList with
            # this expansion
            if sExpansion != self.sUnknownExpansion:
                iThisExpID = IExpansion(sExpansion).id
                iCardCnt = PhysicalCard.selectBy(abstractCardID=oCard.id,
                        expansionID=iThisExpID).count()
            else:
                iCardCnt = PhysicalCard.selectBy(abstractCardID=oCard.id,
                        expansionID=None).count()
            return iCardCnt > 0
        else:
            # Not editable, and iCnt == 0, so remove
            return False

    def get_add_card_expansion_info(self, oCard, dExpanInfo):
        """Get the expansions to list for a newly added card"""
        if not self.bExpansions:
            return []
        if self.bEditable:
            aAddedExpansions = []
            for oPC in PhysicalCard.selectBy(abstractCardID=oCard.id):
                sExpName = self.get_expansion_name(oPC.expansion)
                if sExpName not in aAddedExpansions:
                    # Only each expansion once
                    aAddedExpansions.append(sExpName)
        else:
            aAddedExpansions = dExpanInfo.keys()
        return aAddedExpansions

    def get_exp_name_from_path(self, oPath):
        """
        Get the expansion information from the model, returing None
        if this is not at a level where the expansion is known.
        """
        oIter = self.get_iter(oPath)
        if self.iter_depth(oIter) not in [2, 3]:
            return None
        sName = None
        if self.iExtraLevelsMode in [SHOW_EXPANSIONS,
                EXPANSIONS_AND_CARD_SETS] and self.iter_depth(oIter) == 2:
            sName = self.get_name_from_iter(oIter)
        elif self.iExtraLevelsMode == CARD_SETS_AND_EXPANSIONS and \
                self.iter_depth(oIter) == 3:
            sName = self.get_name_from_iter(oIter)
        elif self.iExtraLevelsMode == EXPANSIONS_AND_CARD_SETS and \
                self.iter_depth(oIter) == 3:
            # Need to get information from the parent level
            sName = self.get_name_from_iter(self.iter_parent(oIter))
        return sName

    def get_all_names_from_path(self, oPath):
        """Get all the relevant names from the path (cardname, expansion
           and card set), returning None for any that can't be determined.

           This is mainly used by the button signals for editing.
           """
        oIter = self.get_iter(oPath)
        iDepth = self.iter_depth(oIter)
        if iDepth == 0:
            # Top Level item, so no info at all
            return None, None, None
        sCardName = self.get_name_from_iter(self.get_iter(norm_path(
            oPath)[0:2]))
        sExpName = None
        sCardSetName = None
        # Get the expansion name
        if self.iExtraLevelsMode in [SHOW_EXPANSIONS,
                EXPANSIONS_AND_CARD_SETS]:
            if iDepth == 2:
                sExpName = self.get_name_from_iter(oIter)
            elif iDepth == 3:
                sExpName = self.get_name_from_iter(self.get_iter(norm_path(
                    oPath)[0:3]))
        elif self.iExtraLevelsMode == CARD_SETS_AND_EXPANSIONS and \
                iDepth == 3:
            sExpName = self.get_name_from_iter(oIter)
        # Get the card set name
        if self.iExtraLevelsMode in [SHOW_CARD_SETS,
                CARD_SETS_AND_EXPANSIONS]:
            if iDepth == 2:
                sCardSetName = self.get_name_from_iter(oIter)
            elif iDepth == 3:
                sCardSetName = self.get_name_from_iter(self.get_iter(norm_path(
                    oPath)[0:3]))
        elif self.iExtraLevelsMode == EXPANSIONS_AND_CARD_SETS and \
                iDepth == 3:
            sCardSetName = self.get_name_from_iter(oIter)
        return sCardName, sExpName, sCardSetName

    def _init_expansions(self, dExpanInfo, oAbsCard):
        """Initialise the expansion dict for a card"""
        if self.bEditable:
            for oRarityPair in oAbsCard.rarity:
                dExpanInfo.setdefault(
                        self.get_expansion_name(oRarityPair.expansion), 0)
            dExpanInfo.setdefault(self.sUnknownExpansion, 0)

    def _init_abs(self, dAbsCards, oAbsCard):
        """Initialize the entry for oAbsCard in dAbsCards"""
        if oAbsCard not in dAbsCards:
            dAbsCards[oAbsCard] = CardSetModelRow(self.bEditable,
                    self.iExtraLevelsMode)
            self._init_expansions(dAbsCards[oAbsCard].dExpansions, oAbsCard)

    def _get_child_filters(self):
        """Get the filters for the child card sets of this card set."""
        # pylint: disable-msg=E1101
        # SQLObject + PyProtocols confuse pylint
        dChildFilters = {}
        if self.iExtraLevelsMode in [SHOW_CARD_SETS, EXPANSIONS_AND_CARD_SETS,
                CARD_SETS_AND_EXPANSIONS] or self.iShowCardMode == CHILD_CARDS:
            # Pre-select cards for child card sets
            aChildren = [x.name for x in
                    PhysicalCardSet.selectBy(parentID=self._oCardSet.id,
                        inuse=True)]
            for sName in aChildren:
                dChildFilters[sName] = PhysicalCardSetFilter(sName)
        return dChildFilters

    def grouped_card_iter(self, oCardIter):
        """
        Handles the differences in the way AbstractCards and PhysicalCards
        are grouped and returns a triple of get_card (the function used to
        retrieve a card from an item), get_card_count (the function used to
        retrieve a card count from an item) and oGroupedIter (an iterator
        over the card groups)
        """
        # Define iterable and grouping function based on cardclass
        aAbsCards = []
        dAbsCards = {}
        dChildFilters = self._get_child_filters()

        # pylint: disable-msg=E1101
        # SQLObject + PyProtocols confuse pylint
        oCurFilter = self.get_current_filter()
        if oCurFilter is None:
            oCurFilter = NullFilter()

        if self._oCardSet.parent:
            oParentFilter = FilterAndBox([oCurFilter,
                PhysicalCardSetFilter(self._oCardSet.parent.name)])
            oParentIter = oParentFilter.select(self.cardclass).distinct()
        else:
            oParentFilter = None
            oParentIter = []

        # Other card show modes
        if self.iShowCardMode != THIS_SET_ONLY:
            # TODO: Revisit the logic once Card Count filters are fixed
            if self.iShowCardMode == ALL_CARDS:
                oExtraCardIter = oCurFilter.select(PhysicalCard).distinct()
            elif self.iShowCardMode == PARENT_CARDS and self._oCardSet.parent:
                # It's tempting to use get_card_iterator here, but that
                # obviously doesn't work because of _oBaseFilter
                oExtraCardIter = oParentIter
            elif self.iShowCardMode == CHILD_CARDS and dChildFilters:
                oChildFilter = MultiPhysicalCardSetMapFilter(dChildFilters)
                oFullFilter = FilterAndBox([oCurFilter, oChildFilter])
                oExtraCardIter = oFullFilter.select(self.cardclass).distinct()
            else:
                oExtraCardIter = oCardIter

            for oCard in oExtraCardIter:
                oAbsCard = IAbstractCard(oCard)
                oPhysCard = IPhysicalCard(oCard)
                self._init_abs(dAbsCards, oAbsCard)
                dAbsCards[oAbsCard].dExpansions.setdefault(
                        self.get_expansion_name(oPhysCard.expansion), 0)
                dExpanInfo = dAbsCards[oAbsCard].dExpansions
                dChildInfo = dAbsCards[oAbsCard].dChildCardSets
                if not dChildInfo and self.iExtraLevelsMode in [
                        SHOW_CARD_SETS, EXPANSIONS_AND_CARD_SETS,
                        CARD_SETS_AND_EXPANSIONS]:
                    self.get_child_set_info(oAbsCard, dChildInfo, dExpanInfo,
                            dChildFilters)

        for oCard in oCardIter:
            # pylint: disable-msg=E1101
            # sqlobject confuses pylint
            oPhysCard = IPhysicalCard(oCard)
            sExpName = self.get_expansion_name(oPhysCard.expansion)
            oAbsCard = IAbstractCard(oPhysCard)
            aAbsCards.append(oAbsCard)
            self._init_abs(dAbsCards, oAbsCard)
            dAbsCards[oAbsCard].iCount += 1
            dChildInfo = dAbsCards[oAbsCard].dChildCardSets
            dExpanInfo = dAbsCards[oAbsCard].dExpansions
            if self.iExtraLevelsMode == SHOW_EXPANSIONS or \
                    self.iExtraLevelsMode == EXPANSIONS_AND_CARD_SETS:
                dExpanInfo.setdefault(sExpName, 0)
                dExpanInfo[sExpName] += 1
            if self.iExtraLevelsMode in [SHOW_CARD_SETS,
                    EXPANSIONS_AND_CARD_SETS, CARD_SETS_AND_EXPANSIONS] and \
                    not dChildInfo:
                # Don't re-filter for repeated abstract cards
                self.get_child_set_info(oAbsCard, dChildInfo, dExpanInfo,
                        dChildFilters)
            if self.iExtraLevelsMode == EXPANSIONS_AND_CARD_SETS:
                dChildInfo.setdefault(sExpName, {})

        self._add_parent_info(dAbsCards, oParentIter)

        aCards = list(dAbsCards.iteritems())
        aCards.sort(lambda x, y: cmp(x[0].name, y[0].name))

        # Iterate over groups
        return (self.groupby(aCards, get_card), aAbsCards)

    def get_child_set_info(self, oAbsCard, dChildInfo, dExpanInfo,
            dChildFilters):
        """Fill in info about the child card sets for the grouped iterator"""
        # pylint: disable-msg=E1101
        # Pyprotocols confuses pylint
        oThisCardFilter = SpecificCardIdFilter(oAbsCard.id)
        for sCardSetName, oFilter in dChildFilters.iteritems():
            oFullFilter = FilterAndBox([oThisCardFilter, oFilter])
            aChildCards = oFullFilter.select(self.cardclass).distinct()
            if self.iExtraLevelsMode == SHOW_CARD_SETS or \
                    self.iExtraLevelsMode == CARD_SETS_AND_EXPANSIONS:
                iChildCnt = aChildCards.count()
                if iChildCnt > 0 or self.iShowCardMode == ALL_CARDS or \
                        self.bEditable:
                    # FIXME: Does this check do what the user would expect?
                    dChildInfo.setdefault(sCardSetName, iChildCnt)
                    if self.iExtraLevelsMode == CARD_SETS_AND_EXPANSIONS:
                        dExpanInfo.setdefault(sCardSetName, {})
                        self._init_expansions(dExpanInfo[sCardSetName],
                                oAbsCard)
                        for oCSCard in aChildCards:
                            oThisPhysCard = IPhysicalCard(oCSCard)
                            sExpName = self.get_expansion_name(
                                    oThisPhysCard.expansion)
                            dExpanInfo[sCardSetName].setdefault(sExpName, 0)
                            dExpanInfo[sCardSetName][sExpName] += 1
            elif self.iExtraLevelsMode == EXPANSIONS_AND_CARD_SETS:
                if self.bEditable:
                    for oRarityPair in oAbsCard.rarity:
                        sExpName = self.get_expansion_name(
                                oRarityPair.expansion)
                        dChildInfo.setdefault(sExpName, {})
                        dChildInfo[sExpName].setdefault(sCardSetName, 0)
                    dChildInfo.setdefault(self.sUnknownExpansion, {})
                    dChildInfo[self.sUnknownExpansion].setdefault(
                            sCardSetName, 0)
                for oCSCard in aChildCards:
                    oThisPhysCard = IPhysicalCard(oCSCard)
                    sExpName = self.get_expansion_name(oThisPhysCard.expansion)
                    dChildInfo.setdefault(sExpName, {})
                    dChildInfo[sExpName].setdefault(sCardSetName, 0)
                    dChildInfo[sExpName][sCardSetName] += 1

    def _add_parent_info(self, dAbsCards, oParentIter):
        """Add the parent count info into the mix"""
        # pylint: disable-msg=E1101
        # Pyprotocols confuses pylint
        if self.iParentCountMode == IGNORE_PARENT or not self._oCardSet.parent:
            # No point in anything at all
            return
        oInUseFilter = None
        if self.iParentCountMode == MINUS_SETS_IN_USE:
            aChildren = [x.name for x in
                    PhysicalCardSet.selectBy(parentID=self._oCardSet.parent.id,
                        inuse=True)]
            if aChildren:
                oInUseFilter = MultiPhysicalCardSetMapFilter(aChildren)
        for oAbsCard in dAbsCards:
            dParentExp = dAbsCards[oAbsCard].dParentExpansions
            if self.iParentCountMode == MINUS_THIS_SET:
                dAbsCards[oAbsCard].iParentCount = -dAbsCards[oAbsCard].iCount
                for sExpansion, iCnt in \
                        dAbsCards[oAbsCard].dExpansions.iteritems():
                    dParentExp[sExpansion] = -iCnt
            elif oInUseFilter:
                oFullFilter = FilterAndBox([SpecificCardIdFilter(oAbsCard.id),
                    oInUseFilter])
                aChildCards = [IPhysicalCard(x) for x in
                        oFullFilter.select(self.cardclass).distinct()]
                for oPhysCard in aChildCards:
                    dAbsCards[oAbsCard].iParentCount -= 1
                    sExpansion = self.get_expansion_name(oPhysCard.expansion)
                    dParentExp.setdefault(sExpansion, 0)
                    dParentExp[sExpansion] -= 1
        for oCard in oParentIter:
            # pylint: disable-msg=E1101
            # Pyprotocols confuses pylint
            oAbsCard = IAbstractCard(oCard)
            if oAbsCard in dAbsCards:
                oPhysCard = IPhysicalCard(oCard)
                sExpansion = self.get_expansion_name(oPhysCard.expansion)
                dParentExp = dAbsCards[oAbsCard].dParentExpansions
                dAbsCards[oAbsCard].iParentCount += 1
                dParentExp.setdefault(sExpansion, 0)
                dParentExp[sExpansion] += 1

    def _remove_sub_iters(self, sCardName):
        """Remove the expansion iters for sCardName"""
        for sValue in self._dNameSecondLevel2Iter[sCardName]:
            if self._dName2nd3rdLevel2Iter.has_key((sCardName, sValue)):
                for oIter in self._dName2nd3rdLevel2Iter[(sCardName, sValue)]:
                    self.remove(oIter)
                del self._dName2nd3rdLevel2Iter[(sCardName, sValue)]
            for oIter in self._dNameSecondLevel2Iter[sCardName][sValue]:
                self.remove(oIter)
        del self._dNameSecondLevel2Iter[sCardName]

    def inc_card(self, oPhysCard):
        """Increase the count for the card oPhysCard, adding a new
           card entry if nessecary."""
        sCardName = oPhysCard.abstractCard.name
        if not self._dName2Iter.has_key(sCardName):
            # new card
            self.add_new_card(oPhysCard)
        else:
            self.alter_card_count(oPhysCard, +1)

    def dec_card(self, oPhysCard):
        """Decrease the count for the card oPhysCard, removing it from the
           view if needed."""
        sCardName = oPhysCard.abstractCard.name
        if self._dName2Iter.has_key(sCardName):
            self.alter_card_count(sCardName, -1)
            if not self.check_card_stats(sCardName):
                self.remove_card(sCardName)
            else:
                self.alter_card_count(oPhysCard, +1)

    def alter_card_expansion_count(self, sCardName, sExpansion, iChg):
        """Adjust the count for the given card + expansion combination by
           iChg."""
        # Need to readjust inc, dec flags for all these cards
        oCard = IAbstractCard(sCardName)
        bDelDictEntry = False
        if not self._dNameSecondLevel2Iter.has_key(sCardName):
            # Can be called by CardSetController with non-existant card
            return
        for sThisExp, aList in \
                self._dNameSecondLevel2Iter[sCardName].iteritems():
            for oIter in aList:
                iCnt = self.get_int_value(oIter, 1)
                if sThisExp == sExpansion:
                    iCnt += iChg
                bIncCard, bDecCard = self.check_inc_dec_expansion(iCnt)
                if self.check_expansion_iter_stays(oCard, sThisExp, iCnt):
                    self.set(oIter,
                            1, self.format_count(iCnt),
                            2, self.format_parent_count(iCnt, 0),
                            3, bIncCard,
                            4, bDecCard)
                else:
                    self.remove(oIter)
                    bDelDictEntry = True
        if bDelDictEntry:
            del self._dNameSecondLevel2Iter[sCardName][sExpansion]

        # Notify Listeners
        for oListener in self.dListeners:
            oListener.alter_card_expansion_count(oCard, sExpansion, iChg)

    def alter_card_count(self, oPhysCard, iChg):
        """
        Alter the card count of a card which is in the
        current list (i.e. in the card set and not filtered
        out) by iChg.
        """
        # pylint: disable-msg=E1101
        # PyProtocols confuses pylint here
        oCard = IAbstractCard(oPhysCard)
        sCardName = oCard.name
        bRemove = False
        for oIter in self._dName2Iter[sCardName]:
            oGrpIter = self.iter_parent(oIter)
            iCnt = self.get_int_value(oIter, 1) + iChg
            iGrpCnt = self.get_int_value(oGrpIter, 1) + iChg
            self.set(oIter, 1, self.format_count(iCnt))

            if self.check_iter_stays(oIter):
                # FIXME: fix parent card formatting, update children, etc.
                bIncCard, bDecCard = self.check_inc_dec_card(iCnt)
                self.set(oIter, 3, bIncCard)
                self.set(oIter, 4, bDecCard)
            else:
                bRemove = True
                if self._dNameSecondLevel2Iter.has_key(sCardName):
                    self._remove_sub_iters(sCardName)
                self.remove(oIter)

            if iGrpCnt > 0:
                self.set(oGrpIter, 1, self.format_count(iGrpCnt))
            else:
                sGroupName = self.get_value(oGrpIter, 0)
                del self._dGroupName2Iter[sGroupName]
                self.remove(oGrpIter)

        if bRemove:
            del self._dName2Iter[sCardName]

        if self.oEmptyIter and iChg > 0:
            # Can no longer be empty
            self.remove(self.oEmptyIter)
            self.oEmptyIter = None
        elif iChg < 0 and not self._dName2Iter:
            # FIXME: fix parent count
            self.oEmptyIter = self.append(None)
            sText = self._get_empty_text()
            self.set(self.oEmptyIter, 0, sText, 1, self.format_count(0), 2,
                    '0', 3, False, 4, False)

        # Notify Listeners
        for oListener in self.dListeners:
            oListener.alter_card_count(oCard, iChg)

    def add_new_card(self, oPhysCard):
        # pylint: disable-msg=R0914
        # we use many local variables for clarity
        """
        If the card oPhysCard is not in the current list
        (i.e. is not in the card set or is filtered out)
        see if it should be filtered out or if it should be
        visible. If it should be visible, add it to the appropriate
        groups.
        """
        oFilter = self.combine_filter_with_base(self.get_current_filter())
        oAbsCard = IAbstractCard(oPhysCard)
        if self.bEditable:
            oFullFilter = FilterAndBox([SpecificCardIdFilter(oAbsCard),
                oFilter])
            # Checking on the physical card picks up filters on the physical
            # expansion - since we show all expansions when editing, checking
            # on the physical card when the list is editable doesn't behave as
            # one would expect, so we only check the abstract card.
        else:
            oFullFilter = FilterAndBox([SpecificPhysCardIdFilter(oPhysCard),
                oFilter])
        oCardIter = oFullFilter.select(self.cardclass).distinct()

        bVisible = oCardIter.count() > 0

        # pylint: disable-msg=W0612
        # Not interested in aAbsCards here, but we need the GroupedIter
        oGroupedIter, aAbsCards = self.grouped_card_iter(oCardIter)
        # Iterate over groups
        for sGroup, oGroupIter in oGroupedIter:
            # Check for null group
            if sGroup is None:
                sGroup = '<< None >>'

            # Find Group Section
            if self._dGroupName2Iter.has_key(sGroup):
                oSectionIter = self._dGroupName2Iter[sGroup]
                iGrpCnt = self.get_int_value(oSectionIter, 1)
            else:
                oSectionIter = self.append(None)
                self._dGroupName2Iter[sGroup] = oSectionIter
                iGrpCnt = 0
                self.set(oSectionIter,
                    0, sGroup,
                    1, self.format_count(iGrpCnt),
                    2, self.format_parent_count(iGrpCnt, 0),
                )

            # Add Cards
            for oCard, oRow in oGroupIter:
                # Due to the various view modes, we aren't assured of
                # getting back only the new card from get_grouped_iterator,
                # so this check is needed
                # pylint: disable-msg=E1101
                # PyProtocols confuses pylint
                if oAbsCard.id != oCard.id:
                    continue
                iCnt = oRow.get_card_count()
                iGrpCnt += iCnt
                oChildIter = self.append(oSectionIter)
                bIncCard, bDecCard = self.check_inc_dec_card(iCnt)
                self.set(oChildIter,
                    0, oCard.name,
                    1, self.format_count(iCnt),
                    2, self.format_parent_count(iCnt, 0),
                    3, bIncCard,
                    4, bDecCard
                )
                self._dName2Iter.setdefault(oCard.name, []).append(oChildIter)
                # Handle as for loading
                self._add_children(oChildIter, oRow)

            # Update Group Section
            self.set(oSectionIter,
                1, self.format_count(iGrpCnt),
            )

        if self.oEmptyIter and oCardIter.count() > 0:
            # remove previous note
            self.remove(self.oEmptyIter)
            self.oEmptyIter = None

        # Notify Listeners
        for oListener in self.dListeners:
            oListener.add_new_card(oAbsCard, bVisible)

    def update_to_new_db(self, sSetName):
        """Update internal card set to the new DB."""
        self._oCardSet = IPhysicalCardSet(sSetName)
        self._oBaseFilter = PhysicalCardSetFilter(sSetName)

    def changes_with_parent(self):
        """Utility function. Returns true if the parent card set influences
           the currently visible set of cards."""
        return self.iParentCountMode != IGNORE_PARENT or \
                self.iShowCardMode == PARENT_CARDS

    def changes_with_children(self):
        """Utiltiy function. Returns true if changes to the child card sets
           influence the display."""
        return self.iShowCardMode == CHILD_CARDS or self.iExtraLevelsMode \
                in [SHOW_CARD_SETS, EXPANSIONS_AND_CARD_SETS,
                        CARD_SETS_AND_EXPANSIONS]

    def changes_with_siblings(self):
        """Utility function. Returns true if changes to the sibling card sets
           influence the display."""
        return self.iParentCountMode == MINUS_SETS_IN_USE

    def inc_sibling_count(self, oPhysCard):
        """Update to an increase in the number of sibling cards."""
        sCardName = oPhysCard.abstractCard.name
        sExpName = self.get_expansion_name(oPhysCard.expansion)
        if not self._dName2Iter.has_key(sCardName):
            # The card isn't visible, so do nothing
            return
        # This is nly called when iParentCountMode == MINUS_SETS_IN_USE,
        # So this decreases the available pool of parent cards
        # There's no possiblity of this deleting a card from the model
        self.alter_parent_card_count(sCardName, sExpName, -1, False)

    def dec_sibling_count(self, oPhysCard):
        """Update to an increase in the number of sibling cards."""
        sCardName = oPhysCard.abstractCard.name
        sExpName = self.get_expansion_name(oPhysCard.expansion)
        if not self._dName2Iter.has_key(sCardName):
            # The card isn't visible, so do nothing
            return
        # This is only called when iParentCountMode == MINUS_SETS_IN_USE,
        # So this increase the available pool of parent cards
        # There's no possiblity of this adding a card to the model (checked
        # above)
        self.alter_parent_card_count(sCardName, sExpName, +1, False)

    def inc_parent_count(self, oPhysCard):
        """Decrease the parent count for the given physical card"""
        sCardName = oPhysCard.abstractCard.name
        sExpName = self.get_expansion_name(oPhysCard.expansion)
        if not self._dName2Iter.has_key(sCardName):
            # Card isn't shown, so need to add it
            self.add_new_card(oPhysCard)
        else:
            self.alter_parent_count(sCardName, sExpName, +1)

    def dec_parent_count(self, oPhysCard):
        """Decrease the parent count for the given physical card"""
        sCardName = oPhysCard.abstractCard.name
        if not self._dName2Iter.has_key(sCardName):
            # Card isn't shown, so nothing to do
            return
        sExpName = self.get_expansion_name(oPhysCard.expansion)
        self.alter_parent_count(sCardName, sExpName, -1)

    def alter_parent_count(self, sCardName, sExpName, iChg, bCheckIter=True):
        """Alter the parent count by iChg

           if bCheckIter is False, we don't check whether anything should
           be removed from the model. This is used for sibling card set
           changes.
           """
        bRemove = False
        for oIter in self._dName2Iter[sCardName]:
            oGrpIter = self.iter_parent(oIter)
            iParGrpCnt = self.get_int_value(oGrpIter, 2) + iChg
            iParCnt = self.get_int_value(oIter, 2) + iChg
            iGrpCnt = self.get_int_value(oGrpIter, 1)
            iCnt = self.get_int_value(oIter, 1)
            self.set(oIter, 2, self.format_parent_count(iCnt, iParCnt))
            self.set(oGrpIter, 2, self.format_parent_count(iGrpCnt,
                iParGrpCnt))
            if self.check_iter_stays(oIter) or not bCheckIter:
                # FIXME: Update the children
                bRemoveChild = False
            else:
                bRemove = True # Delete from cache after the loop
                self._remove_sub_iters(sCardName)
                self.remove(oIter)
                if not self.check_iter_stays(oGrpIter):
                    self.remove(oGrpIter)
        if bRemove:
            del self._dName2Iter[sCardName]

    def inc_child_count(self, oPhysCard, sCardSetName):
        """Add the card oPhysCard in the card set sCardSetName to the model."""
        pass

    def dec_child_count(self, oPhysCard, sCardSetName):
        """Remove the card oPhysCard in the card set sCardSetName
           from the model."""
        pass

    def check_iter_stays(self, oIter):
        """Check if we need to remove a given row or not"""
        # FIXME: implement
        # Conditions for removal vary with the cards shown and the editable
        # mode
        if self.iShowCardMode == ALL_CARDS:
            return True # We don't remove entries
        iCnt = self.get_int_value(oIter, 1)
        iDepth = self.iter_depth(oIter)
        if iDepth > 1:
            oCardPath = norm_path(self.get_path(oIter))[0:2]
            iCardCnt = self.get_int_value(self.get_iter(oCardPath), 1)
        else:
            iCardCnt = iCnt
        if iCnt > 0 and iCardCnt > 0:
            # We never remove a entry for which the count + card count are
            # non-zero
            return True
        bResult = False
        if self.iShowCardMode == THIS_SET_ONLY:
            if self.bEditable and iCardCnt > 0:
                # We never remove children from a editable list if the
                # actual card count is non-zero
                bResult = True
            # else remove
        elif self.iShowCardMode == PARENT_CARDS:
            # Remove card if count zero and card is not in parent set
            pass
        elif self.iShowCardMode == CHILD_CARDS:
            # remove card if count zero and card is not in child card sets
            pass
        return bResult

    def get_drag_info_from_path(self, oPath):
        """Get card name and expansion information from the path for the
           drag and drop code.

           This returns cardname of None if the path is not a card in this
           card set, such as a top-level item or card in a child card set.
           """
        oIter = self.get_iter(oPath)
        iDepth = self.iter_depth(oIter)
        if iDepth == 2 and self.iExtraLevelsMode == SHOW_EXPANSIONS:
            sName = self.get_name_from_iter(self.get_iter(
                norm_path(oPath)[0:2]))
            sExpansion = self.get_value(oIter, 0)
        elif iDepth == 1:
            sName = self.get_name_from_iter(oIter)
            sExpansion = None
        else:
            sName = None
            sExpansion = None
        iCount = self.get_int_value(oIter, 1)
        return sName, sExpansion, iCount, iDepth

    def get_drag_child_info(self, oPath):
        """Get the expansion information for the card at oPath.

           Always returns the expansions, regaredless of iExtraLevelsMode.
           """
        oIter = self.get_iter(oPath)
        iDepth = self.iter_depth(oIter)
        if iDepth != 1:
            return {} # Not at the right level
        dResult = {}
        if self.iExtraLevelsMode == SHOW_EXPANSIONS:
            # Can read off the data from the model, so do so
            oChildIter = self.iter_children(oIter)
            while oChildIter:
                oChildPath = self.get_path(oChildIter)
                sCardName, sExpansion, iCount, iDepth = \
                        self.get_drag_info_from_path(oChildPath)
                dResult[sExpansion] = iCount
                oChildIter = self.iter_next(oChildIter)
        else:
            # Need to get expansion info from the database
            sCardName = self.get_name_from_iter(self.get_iter(oPath))
            oFilter = SpecificCardFilter(sCardName)
            oCardIter = self.get_card_iterator(oFilter)
            # pylint: disable-msg=E1101
            # Pyprotocols confuses pylint
            for oCard in oCardIter:
                oPhysCard = IPhysicalCard(oCard)
                sExpName = self.get_expansion_name(oPhysCard.expansion)
                dResult.setdefault(sExpName, 0)
                dResult[sExpName] += 1
        return dResult
