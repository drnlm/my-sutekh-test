# AnalyzeCardList.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Dialog to display deck analysis software
# Copyright 2006, 2007 Neil Muller <drnlmuller+sutekh@gmail.com>,
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# GPL - see COPYING for details
"""
Display interesting statistics and properties of the card set
"""

import gtk
from sutekh.core.SutekhObjects import PhysicalCardSet, AbstractCardSet, IAbstractCard
from sutekh.core.Filters import CardTypeFilter
from sutekh.gui.PluginManager import CardListPlugin
from sutekh.gui.SutekhDialog import SutekhDialog

class AnalyzeCardList(CardListPlugin):
    """
    Plugin to analyze card sets.
    Displays various interesting stats, and does
    a Happy Family analysis of the deck
    """
    dTableVersions = {PhysicalCardSet : [3, 4],
            AbstractCardSet : [3]}
    aModelsSupported = [PhysicalCardSet,
            AbstractCardSet]

    # Should this be defined in SutekhObjects??
    dTitleVoteMap = {
            'Primogen' : 1,
            'Prince' : 2,
            'Justicar' : 3,
            'Inner Circle' : 4,
            'Priscus' : 3,
            'Bishop' : 1,
            'Archbishop' : 2,
            'Cardinal' : 3,
            'Regent' : 4,
            'Independent with 1 vote' : 1,
            'Independent with 2 votes' : 2,
            'Independent with 3 votes' : 3,
            'Magaji' : 2,
            }

    def _percentage(self, iNum, iTot, sDesc):
        "Utility function for calculating percentages"
        if iTot>0:
            fPrec = iNum/float(iTot)
        else:
            fPrec = 0.0
        return '(' + str(fPrec*100).ljust(5)[:5] + "% of " + sDesc + ')'

    def _get_abstract_cards(self, aCards):
        "Get the asbtract cards given the list of names"
        return [IAbstractCard(x) for x in aCards]

    def _get_sort_key(self, x):
        "Ensure we sort on the right key"
        return x[1][0]

    def get_menu_item(self):
        """
        Overrides method from base class.
        """
        if not self.check_versions() or not self.check_model_type():
            return None
        iAnalyze = gtk.MenuItem("Analyze Deck")
        iAnalyze.connect("activate", self.activate)
        return iAnalyze

    def get_desired_menu(self):
        "Menu to associate with"
        return "Plugins"

    def activate(self, oWidget):
        "Run the plugin"
        dlg = self.make_dialog()
        dlg.run()

    def make_dialog(self):
        "Create the actual dialog, and populate it"
        name = "Analysis of Card List"
        deckName = self.view.sSetName
        oCS = self._cModelType.byName(self.view.sSetName)

        sComment = oCS.comment.replace('&', '&amp;')
        sAuthor = oCS.author

        dlg = SutekhDialog(name, self.parent,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_OK))
        dlg.connect("response", lambda dlg, resp: dlg.destroy())
        oNotebook = gtk.Notebook()
        # Oh, popup_enable and scrollable - how I adore thee
        oNotebook.set_scrollable(True)
        oNotebook.popup_enable()

        oMainLabel = gtk.Label()
        oMainLabel.set_line_wrap(True)
        oMainLabel.set_width_chars(60)
        oHappyFamiliesLabel = gtk.Label()
        oVampiresLabel = gtk.Label()
        oImbuedLabel = gtk.Label()
        oMastersLabel = gtk.Label()
        oCombatLabel = gtk.Label()
        oActionsLabel = gtk.Label()
        oActModLabel = gtk.Label()
        oRetainersLabel = gtk.Label()
        oAlliesLabel = gtk.Label()
        oEventsLabel = gtk.Label()
        oPowersLabel = gtk.Label()
        oConvictionsLabel = gtk.Label()
        oReactionLabel = gtk.Label()
        oEquipmentLabel = gtk.Label()
        oPoliticalLabel = gtk.Label()

        oNotebook.append_page(oMainLabel, gtk.Label('Basic Info'));
        oNotebook.append_page(oHappyFamiliesLabel, gtk.Label('Happy Families Analysis'));
        oNotebook.append_page(oVampiresLabel, gtk.Label('Vampires'));
        oNotebook.append_page(oAlliesLabel, gtk.Label('Allies'));
        oNotebook.append_page(oMastersLabel, gtk.Label('Master Cards'));
        oNotebook.append_page(oCombatLabel, gtk.Label('Combat Cards'));
        oNotebook.append_page(oActionsLabel, gtk.Label('Actions'));
        oNotebook.append_page(oPoliticalLabel, gtk.Label('Political Actions'));
        oNotebook.append_page(oActModLabel, gtk.Label('Action Modifiers'));
        oNotebook.append_page(oReactionLabel, gtk.Label('Reactions'));
        oNotebook.append_page(oRetainersLabel, gtk.Label('Retainers'))
        oNotebook.append_page(oEquipmentLabel, gtk.Label('Equipment'));
        oNotebook.append_page(oEventsLabel, gtk.Label('Events'));
        oNotebook.append_page(oImbuedLabel, gtk.Label('Imbued'));
        oNotebook.append_page(oPowersLabel, gtk.Label('Powers'));
        oNotebook.append_page(oConvictionsLabel, gtk.Label('Convictions'));

        sMainText = "Analysis Results for deck : <b>" + deckName + "</b>\nby <i>"+sAuthor+"</i>\n"+sComment+"\n"

        self.iMaxGroup = -500
        self.iMinGroup = 500
        self.iNumberMult = 0
        self.dCryptDisc = {}

        # Split out the card types of interest
        aAllCards = list(self.model.getCardIterator(None))
        self.iTotNumber = len(aAllCards)
        # Split the cards by type
        # Crypt Cards
        aVampireCards = list(self.model.getCardIterator(CardTypeFilter('Vampire')))
        self.iNumberVampires = len(aVampireCards)
        aImbuedCards = list(self.model.getCardIterator(CardTypeFilter('Imbued')))
        self.iNumberImbued = len(aImbuedCards)
        self.iCryptSize = self.iNumberImbued + self.iNumberVampires

        oVampiresLabel.set_markup(self.process_vampire(aVampireCards))
        oImbuedLabel.set_markup(self.process_imbued(aImbuedCards))

        # Library Cards
        aCombatCards = list(self.model.getCardIterator(CardTypeFilter('Combat')))
        self.iNumberCombats = len(aCombatCards)
        aReactionCards = list(self.model.getCardIterator(CardTypeFilter('Reaction')))
        self.iNumberReactions = len(aReactionCards)
        aActionCards = list(self.model.getCardIterator(CardTypeFilter('Action')))
        self.iNumberActions = len(aActionCards)
        aActModCards = list(self.model.getCardIterator(CardTypeFilter('Action Modifier')))
        self.iNumberActMods = len(aActModCards)
        aRetainerCards = list(self.model.getCardIterator(CardTypeFilter('Retainer')))
        self.iNumberRetainers = len(aRetainerCards)
        aAlliesCards = list(self.model.getCardIterator(CardTypeFilter('Ally')))
        self.iNumberAllies = len(aAlliesCards)
        aEquipCards = list(self.model.getCardIterator(CardTypeFilter('Equipment')))
        self.iNumberEquipment = len(aEquipCards)
        aPoliticalCards = list(self.model.getCardIterator(CardTypeFilter('Political Action')))
        self.iNumberPoliticals = len(aPoliticalCards)
        aPowerCards = list(self.model.getCardIterator(CardTypeFilter('Power')))
        self.iNumberPowers = len(aPowerCards)
        aConvictionCards = list(self.model.getCardIterator(CardTypeFilter('Conviction')))
        self.iNumberConvictions = len(aConvictionCards)
        aEventCards = list(self.model.getCardIterator(CardTypeFilter('Event')))
        self.iNumberEvents = len(aEventCards)
        aMasterCards = list(self.model.getCardIterator(CardTypeFilter('Master')))
        self.iNumberMasters = len(aMasterCards)

        self.iNumberLibrary = self.iTotNumber - self.iNumberVampires - self.iNumberImbued

        oCombatLabel.set_markup(self.process_combat(aCombatCards))
        oReactionLabel.set_markup(self.process_reaction(aReactionCards))
        oActModLabel.set_markup(self.process_action_modifier(aActModCards))
        oAlliesLabel.set_markup(self.process_allies(aAlliesCards))
        oEventsLabel.set_markup(self.process_event(aEventCards))
        oActionsLabel.set_markup(self.process_action(aActionCards))
        oPoliticalLabel.set_markup(self.process_political_action(aPoliticalCards))
        oRetainersLabel.set_markup(self.process_retainer(aRetainerCards))
        oEquipmentLabel.set_markup(self.process_equipment(aEquipCards))
        oPowersLabel.set_markup(self.process_power(aPowerCards))
        oConvictionsLabel.set_markup(self.process_conviction(aConvictionCards))
        oMastersLabel.set_markup(self.process_master(aMasterCards))

        oHappyFamiliesLabel.set_markup(self.happyFamiliesAnalysis(aAllCards))

        # Set main notebook text

        sMainText += "Number of Vampires = " + str(self.iNumberVampires) + "\n"
        sMainText += "Number of Imbued = " + str(self.iNumberImbued) + "\n"
        sMainText += "Total Crypt size = " + str(self.iCryptSize) + "\n"
        sMainText += "Minimum Group in Crpyt = " + str(self.iMinGroup) + "\n"
        sMainText += "Maximum Group in Crypt = " + str(self.iMaxGroup) + "\n"

        if self.iCryptSize < 12:
            sMainText += "<span foreground = \"red\">Less than 12 Crypt Cards</span>\n"

        if self.iMaxGroup - self.iMinGroup > 1:
            sMainText += "<span foreground = \"red\">Group Range Exceeded</span>\n"

        sMainText += "Total Library Size = " + str(self.iNumberLibrary) + "\n"

        if self.iNumberLibrary > 0:
            sMainText += "Number of Masters = " + \
                    str(self.iNumberMasters) + ' ' +\
                    self._percentage(self.iNumberMasters,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Combat cards = " + \
                    str(self.iNumberCombats) + ' ' + \
                    self._percentage(self.iNumberCombats,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Action cards = " + \
                    str(self.iNumberActions) + ' ' + \
                    self._percentage(self.iNumberActions,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Political Action cards = " + \
                    str(self.iNumberPoliticals) + ' ' + \
                    self._percentage(self.iNumberPoliticals,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Action Modifiers = " + \
                    str(self.iNumberActMods) + ' ' + \
                    self._percentage(self.iNumberActMods,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Reaction cards = " + \
                    str(self.iNumberReactions) + ' ' + \
                    self._percentage(self.iNumberReactions,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Allies = " + \
                    str(self.iNumberAllies) + ' ' + \
                    self._percentage(self.iNumberAllies,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Retainers = " + \
                    str(self.iNumberRetainers) + ' ' + \
                    self._percentage(self.iNumberAllies,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Equipment cards = " + \
                    str(self.iNumberEquipment) + ' ' + \
                    self._percentage(self.iNumberEquipment,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Event cards = " + \
                    str(self.iNumberEvents) + ' ' + \
                    self._percentage(self.iNumberEvents,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Convictions = " + \
                    str(self.iNumberConvictions) + ' ' + \
                    self._percentage(self.iNumberConvictions,
                            self.iNumberLibrary, "Library") + '\n'
            sMainText += "Number of Powers = " + \
                    str(self.iNumberPowers) + ' ' + \
                    self._percentage(self.iNumberPowers,
                            self.iNumberLibrary, "Library") + '\n'

        sMainText += "Number of Multirole cards = " + \
                str(self.iNumberMult) + ' ' + \
                self._percentage(self.iNumberMult,
                        self.iNumberLibrary, "Library") + '\n'

        oMainLabel.set_markup(sMainText)

        dlg.vbox.pack_start(oNotebook)
        dlg.show_all()

        return dlg


    def get_card_costs(self, aAbsCards):
        """
        Calculate the cost of the list of Abstract Cards
        Return lists of costs, for pool, blood and convictions
        Each list contains: Number with variable cost, Maximum Cost, Total Cost
        """
        dCosts = {}
        for sType in ['blood', 'pool', 'conviction']:
            dCosts.setdefault(sType, [0, 0, 0])
        for oAbsCard in aAbsCards:
            if oAbsCard.cost is not None:
                if oAbsCard.cost == -1:
                    dCosts[oAbsCard.costtype][0] += 1
                else:
                    iMaxCost = dCosts[oAbsCard.costtype][1]
                    dCosts[oAbsCard.costtype][1] = max(iMaxCost, oAbsCard.cost)
                    dCosts[oAbsCard.costtype][2] += oAbsCard.cost
        return dCosts['blood'], dCosts['pool'], dCosts['conviction']

    def process_vampire(self, aCards):
        """Process the list of vampires"""
        dDeckVamps = {}
        dVampCapacity = {}
        dDeckTitles = {}
        dDeckClans = {}
        dDeckDisc = {}

        iTotCapacity = 0
        iNumberUniqueVampires = 0
        iMaxCapacity = -500
        iMinCapacity = 500
        iVampMinGroup = 500
        iVampMaxGroup = -500
        iVotes = 0
        iTitles = 0

        for oAbsCard in self._get_abstract_cards(aCards):
            if oAbsCard.name not in dDeckVamps:
                iNumberUniqueVampires += 1
                dDeckVamps[oAbsCard.name] = 1
            else:
                dDeckVamps[oAbsCard.name] += 1

            self.iMaxGroup = max(self.iMaxGroup, oAbsCard.group)
            self.iMinGroup = min(self.iMinGroup, oAbsCard.group)
            iVampMaxGroup = max(iVampMaxGroup, oAbsCard.group)
            iVampMinGroup = min(iVampMinGroup, oAbsCard.group)

            iTotCapacity += oAbsCard.capacity
            iMaxCapacity = max(iMaxCapacity, oAbsCard.capacity)
            iMinCapacity = min(iMinCapacity, oAbsCard.capacity)

            dVampCapacity.setdefault(oAbsCard.capacity, 0)
            dVampCapacity[oAbsCard.capacity] += 1

            for clan in oAbsCard.clan:
                if clan.name not in dDeckClans:
                    dDeckClans[clan.name] = 1
                else:
                    dDeckClans[clan.name] += 1

            for disc in oAbsCard.discipline:
                if disc.discipline.fullname in dDeckDisc:
                    dDeckDisc[disc.discipline.fullname][0] += 1
                else:
                    dDeckDisc[disc.discipline.fullname] = [1, 0]

                if disc.level == 'superior':
                    dDeckDisc[disc.discipline.fullname][1] += 1

            for title in oAbsCard.title:
                iTitles += 1
                if title.name in dDeckTitles:
                    dDeckTitles[title.name] += 1
                else:
                    dDeckTitles[title.name] = 1

                iVotes+=self.dTitleVoteMap[title.name]

        # Build up Text
        sVampText = "<b>Vampires :</b>\n"
        sVampText += "<span foreground = \"blue\">Basic Crypt stats</span>\n"
        sVampText += "Number of Vampires = " + str(self.iNumberVampires) + \
                self._percentage(self.iNumberVampires, self.iCryptSize, "Crypt") + "\n"
        sVampText += "Number of Unique Vampires = " + str(iNumberUniqueVampires) + "\n"

        if self.iNumberVampires > 0:
            sVampText += "Minimum Group is : " + str(iVampMinGroup) + "\n"
            sVampText += "Maximum Group is : " + str(iVampMaxGroup) + "\n"

            sVampText += "\n<span foreground = \"blue\">Crypt cost</span>\n"
            sVampText += "Cheapest is : " + str(iMinCapacity) + "\n"
            sVampText += "Most Expensive is : " + str(iMaxCapacity) + "\n"
            sVampText += "Average Capacity is : " + str(iTotCapacity / \
                    float(self.iNumberVampires)).ljust(5)[:5] + "\n\n"

            sVampText += "<span foreground = \"blue\">Clans</span>\n"
            for clan, number in dDeckClans.iteritems():
                sVampText += str(number) + " Vampires of clan " + str(clan) + ' ' + \
                        self._percentage(number,
                            self.iCryptSize, "Crypt") + '\n'

            sVampText += "\n<span foreground = \"blue\">Titles</span>\n"

            for title, number in dDeckTitles.iteritems():
                sVampText += str(number) + " vampires with the title " + str(title) \
                           + " (" + str(self.dTitleVoteMap[title]) + ") votes\n"

            sVampText += str(iVotes) + " votes in the crypt. Average votes per vampire is " \
                       + str(iVotes / float(self.iNumberVampires)).ljust(5)[:5] + "\n"

            sVampText += str(iTitles) + " titles in the crypt " + \
                        self._percentage(iTitles,
                            self.iCryptSize, "Crypt") + '\n'

            sVampText += "<span foreground = \"blue\">Disciplines</span>\n"
            for discipline, number in sorted(dDeckDisc.iteritems(),
                    key=self._get_sort_key, reverse=True):
                sVampText += str(number[0])+" Vampires with " + discipline \
                           + ' ' + self._percentage(number[0],
                                   self.iCryptSize, "Crypt") + ", " \
                           + str(number[1]) + " at Superior " + \
                           self._percentage(number[1],
                                   self.iCryptSize, "Crypt") + '\n'
                self.dCryptDisc.setdefault(number[0], [])
                self.dCryptDisc[number[0]].append(discipline)

        return sVampText

    def process_master(self, aCards):
        iClanRequirement = 0
        aAbsCards = self._get_abstract_cards(aCards)
        aBlood, aPool, aConviction = self.get_card_costs(aAbsCards)

        for oAbsCard in aAbsCards:
            if not len(oAbsCard.clan) == 0:
                iClanRequirement += 1

        # Build up Text
        sMasterText = "<b>Master Cards :</b>\n"
        sMasterText += "Number of Masters = " + str(self.iNumberMasters) + ' ' + \
                self._percentage(self.iNumberMasters,
                        self.iNumberLibrary, "Library") + '\n'
        if self.iNumberMasters > 0:
            sMasterText += "Most Expensive Master = " + str(aPool[1]) +'\n'
            sMasterText += "Masters with Variable Cost = " + str(aPool[0]) + ' ' + \
                    self._percentage(aPool[0],
                            self.iNumberMasters, "Masters") + '\n'
            sMasterText += "Average Master Cost = " + str(aPool[2] / \
                    float(self.iNumberMasters)).ljust(5)[:5] + '\n'
            sMasterText += "Number of Masters with a Clan requirement = " + str(iClanRequirement) + ' ' + \
                    self._percentage(iClanRequirement,
                            self.iNumberMasters, "Masters") + '\n'
        return sMasterText

    def process_combat(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sCombatText = "<b>Combat Cards :</b>\n"
        sCombatText += "Number of Combat cards = " + str(self.iNumberCombats) + ' '+ \
                           self._percentage(self.iNumberCombats,
                                   self.iNumberLibrary, "Library") + '\n'
        return sCombatText

    def process_action_modifier(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sActModText = "<b>Action Modifier Cards :</b>\n"
        sActModText += "Number of Action Modifier cards = " + str(self.iNumberActMods) + ' '+ \
                           self._percentage(self.iNumberActMods,
                                   self.iNumberLibrary, "Library") + '\n'
        return sActModText

    def process_reaction(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sReactionText = "<b>Reaction Cards :</b>\n"
        sReactionText += "Number of Reaction cards = " + str(self.iNumberReactions) + ' '+ \
                           self._percentage(self.iNumberReactions,
                                   self.iNumberLibrary, "Library") + '\n'
        return sReactionText

    def process_event(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sEventText = "<b>Event Cards :</b>\n"
        sEventText += "Number of Event cards = " + str(self.iNumberEvents) + ' '+ \
                           self._percentage(self.iNumberEvents,
                                   self.iNumberLibrary, "Library") + '\n'
        return sEventText

    def process_action(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sActionText = "<b>Action Cards :</b>\n"
        sActionText += "Number of Action cards = " + str(self.iNumberActions) + ' '+ \
                           self._percentage(self.iNumberActions,
                                   self.iNumberLibrary, "Library") + '\n'
        return sActionText

    def process_political_action(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sPoliticalText = "<b>Political Cards :</b>\n"
        sPoliticalText += "Number of Political cards = " + str(self.iNumberPoliticals) + ' '+ \
                           self._percentage(self.iNumberPoliticals,
                                   self.iNumberLibrary, "Library") + '\n'
        return sPoliticalText

    def process_allies(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sAlliesText = "<b>Allies Cards :</b>\n"
        sAlliesText += "Number of Allies cards = " + str(self.iNumberAllies) + ' '+ \
                           self._percentage(self.iNumberAllies,
                                   self.iNumberLibrary, "Library") + '\n'
        return sAlliesText


    def process_retainer(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sRetainerText = "<b>Retainer Cards :</b>\n"
        sRetainerText += "Number of Retainer cards = " + str(self.iNumberRetainers) + ' '+ \
                           self._percentage(self.iNumberRetainers,
                                   self.iNumberLibrary, "Library") + '\n'
        return sRetainerText

    def process_equipment(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sEquipmentText = "<b>Equipment Cards :</b>\n"
        sEquipmentText += "Number of Equipment cards = " + str(self.iNumberEquipment) + ' '+ \
                           self._percentage(self.iNumberEquipment,
                                   self.iNumberLibrary, "Library") + '\n'
        return sEquipmentText

    def process_conviction(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sConvictionText = "<b>Conviction Cards :</b>\n"
        sConvictionText += "Number of Conviction cards = " + str(self.iNumberConvictions) + ' '+ \
                           self._percentage(self.iNumberConvictions,
                                   self.iNumberLibrary, "Library") + '\n'
        return sConvictionText

    def process_power(self, aCards):
        for oAbsCard in self._get_abstract_cards(aCards):
            pass

        # Build up Text
        sPowerText = "<b>Power Cards :</b>\n"
        sPowerText += "Number of Power cards = " + str(self.iNumberPowers) + ' '+ \
                           self._percentage(self.iNumberPowers,
                                   self.iNumberLibrary, "Library") + '\n'
        return sPowerText

    def process_imbued(self, aCards):
        dDeckImbued = {}
        dDeckVirt = {}

        iMaxLife = -500
        iMinLife = 500
        iTotLife = 0
        iImbMinGroup = 500
        iImbMaxGroup = -500
        iNumberUniqueImbued = 0

        for oAbsCard in self._get_abstract_cards(aCards):
            if oAbsCard.name not in dDeckImbued:
                iNumberUniqueImbued += 1
                dDeckImbued[oAbsCard.name] = 1
            else:
                dDeckImbued[oAbsCard.name] += 1

            for virtue in oAbsCard.virtue:
                dDeckVirt.setdefault(virtue.fullname, [0])
                # List, so we can use _get_sort_key
                dDeckVirt[virtue.fullname][0] += 1

            self.iMaxGroup = max(self.iMaxGroup, oAbsCard.group)
            self.iMinGroup = min(self.iMinGroup, oAbsCard.group)
            iImbMaxGroup = max(iImbMaxGroup, oAbsCard.group)
            iImbMinGroup = min(iImbMinGroup, oAbsCard.group)

            iTotLife += oAbsCard.life
            iMaxLife = max(iMaxLife, oAbsCard.life)
            iMinLife = min(iMinLife, oAbsCard.life)

        # Build up Text
        sImbuedText = "<b>Imbued</b>\n"
        sImbuedText += "<span foreground = \"blue\">Basic Crypt stats</span>\n"
        sImbuedText += "Number of Imbued = " + str(self.iNumberImbued) + \
                self._percentage(self.iNumberImbued, self.iCryptSize, "Crypt") + "\n"
        sImbuedText += "Number of Uniueq Imbued = " + str(iNumberUniqueImbued) + "\n"
        if self.iNumberImbued > 0:
            sImbuedText += "Minimum Group is : " + str(iImbMinGroup) + "\n"
            sImbuedText += "Maximum Group is : " + str(iImbMaxGroup) + "\n"

            sImbuedText += "\n<span foreground = \"blue\">Crypt cost</span>\n"

            sImbuedText += "Cheapest is : " + str(iMinLife) + "\n"
            sImbuedText += "Most Expensive is : " + str(iMaxLife) + "\n"
            sImbuedText += "Average Life is : " + str(iTotLife / float(self.iNumberImbued)).ljust(5)[:5] + "\n\n"

            for virtue, number in sorted(dDeckVirt.iteritems(),
                    key=self._get_sort_key, reverse=True):
                sImbuedText += str(number[0])+" Imbued with " + virtue \
                           + ' ' + self._percentage(number[0],
                                   self.iCryptSize, "Crypt") + '\n'
                # Treat virtues as inferior disciplines for happy families
                self.dCryptDisc.setdefault(number[0], [])
                self.dCryptDisc[number[0]].append(virtue)

        return sImbuedText

    def happyFamiliesAnalysis(self, aCards):
        dLibDisc = {}

        dLibDisc.setdefault('No Discipline', 0)

        for oAbsCard in self._get_abstract_cards(aCards):
            aTypes = [x.name for x in oAbsCard.cardtype]
            if len(aTypes)>1:
                # Since we examining all the cards, do this here
                self.iNumberMult += 1
            if aTypes[0] != 'Vampire' and aTypes[0] != 'Imbued' \
                    and aTypes[0] != 'Master':
                # Non-Master Library card, so extract disciplines
                if len(oAbsCard.discipline) > 0:
                    for disc in oAbsCard.discipline:
                        dLibDisc.setdefault(disc.discipline.fullname, 0)
                        dLibDisc[disc.discipline.fullname] += 1
                elif len(oAbsCard.virtue) > 0:
                    for virtue in oAbsCard.virtue:
                        dLibDisc.setdefault(virtue.fullname, 0)
                        dLibDisc[virtue.fullname] += 1
                else:
                    dLibDisc['No Discipline'] += 1

        # Build up Text
        sHappyFamilyText = "<b>Happy Families Analysis :</b>\n"
        if self.iNumberImbued > 0:
            sHappyFamilyText += "\n<span foreground = \"red\">This is not optimised for Imbued, and treats them as small vampires</span>\n"

        if self.iCryptSize == 0:
            sHappyFamilyText += "\n<span foreground = \"red\">Need to have a crypt to do the analysis</span>\n"
            return sHappyFamilyText

        iHFMasters = int(round(0.2 * self.iNumberLibrary))

        iNonMasters = self.iNumberLibrary - self.iNumberMasters

        sHappyFamilyText += "\n<b>Master Cards</b>\n"
        sHappyFamilyText += str(self.iNumberMasters) + " Masters " + \
                self._percentage(self.iNumberMasters,
                        self.iNumberLibrary, "Library") + \
                ",\nHappy Families recommends 20%, which would be " + \
                str(iHFMasters) + '  : '

        sHappyFamilyText += "<span foreground = \"blue\">Difference = " + \
                str(abs(iHFMasters - self.iNumberMasters)) + "</span>\n"

        aTopVampireDisc = sorted(self.dCryptDisc.keys(), reverse=True)
        aMajorDisc = []
        for number in aTopVampireDisc:
            for disc in self.dCryptDisc[number]:
                aMajorDisc.append( (number, disc ) )
                dLibDisc.setdefault(disc, 0) # Need to ensure all these are defined

        # TODO - handle case of a == b == c better than currently

        # self.dCryptDisc and dLibDisc have the info we need about the disciplines
        for iNumberToShow in range(2, 5):
            if len(aMajorDisc) >= iNumberToShow:
                sHappyFamilyText += "<b>" + str(iNumberToShow) + " Discipline Case</b>\n"
                fDemon = float(self.iCryptSize)
                for j in range(iNumberToShow):
                    fDemon += aMajorDisc[j][0]
                iHFNoDiscipline = int((iNonMasters * self.iCryptSize / fDemon ))
                iDiff = iNonMasters - iHFNoDiscipline
                aDiscNumbers = []
                for j in range(iNumberToShow):
                    iDisc = int(iNonMasters * aMajorDisc[j][0] / fDemon )
                    aDiscNumbers.append(iDisc)
                    iDiff -= iDisc

                if iDiff > 0:
                    iHFNoDiscipline += iDiff # Shove rounding errors here

                sHappyFamilyText += "Number of Cards requiring No discipline : " + \
                        str( dLibDisc['No Discipline']) + '\n'
                sHappyFamilyText += "Happy Families recommends " + \
                        str(iHFNoDiscipline) + ' : '
                sHappyFamilyText += "<span foreground = \"blue\">Difference = " + \
                        str(abs(iHFNoDiscipline - dLibDisc['No Discipline'])) + "</span>\n"
                for j in range(iNumberToShow):
                    disc = aMajorDisc[j][1]
                    number = aMajorDisc[j][0]
                    sHappyFamilyText += "Number of Cards requiring " + disc + " : " + \
                            str( dLibDisc[disc]) + \
                            " (" + str(aMajorDisc[j][0]) + " crypt members)\n"
                    sHappyFamilyText += "Happy Families recommends " + \
                            str(aDiscNumbers[j]) + '  : '
                    sHappyFamilyText += "<span foreground = \"blue\">Difference = " + \
                            str(abs(aDiscNumbers[j] - dLibDisc[disc])) + "</span>\n"

        return sHappyFamilyText

plugin = AnalyzeCardList
