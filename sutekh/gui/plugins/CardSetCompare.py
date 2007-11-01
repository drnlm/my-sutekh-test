# CardSetCompare.py
# Copyright 2006 Simon Cross <hodgestar@gmail.com>, Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

import gtk
from sutekh.core.SutekhObjects import PhysicalCard, AbstractCardSet,\
                                 PhysicalCardSet, AbstractCard, IAbstractCard
from sutekh.core.Filters import PhysicalCardSetFilter, AbstractCardSetFilter
from sutekh.gui.PluginManager import CardListPlugin
from sutekh.gui.ScrolledList import ScrolledList

class CardSetCompare(CardListPlugin):
    dTableVersions = {AbstractCardSet.sqlmeta.table : [1,2,3],
                      PhysicalCardSet.sqlmeta.table : [1,2,3]}
    aModelsSupported = [AbstractCardSet.sqlmeta.table,
            PhysicalCardSet.sqlmeta.table]
    def getMenuItem(self):
        """
        Overrides method from base class.
        """
        if not self.checkVersions() or not self.checkModelType():
            return None
        iDF = gtk.MenuItem("Compare with another Card Set")
        iDF.connect("activate", self.activate)
        return iDF

    def getDesiredMenu(self):
        return "Plugins"

    def activate(self,oWidget):
        oDlg = self.makeDialog()
        oDlg.run()
        # only do stuff for AbstractCardSets

    def makeDialog(self):
        """
        Create the list of card sets to select
        """
        parent = self.view.getWindow()
        self.oDlg = gtk.Dialog("Choose Card Set to Compare with",parent,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          (gtk.STOCK_OK, gtk.RESPONSE_OK,
                           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        if self._sModelType == AbstractCardSet.sqlmeta.table:
            oSelect = AbstractCardSet.select().orderBy('name')
            self.csFrame = ScrolledList('Abstract Card Sets')
        elif self._sModelType == PhysicalCardSet.sqlmeta.table:
            oSelect = PhysicalCardSet.select().orderBy('name')
            self.csFrame = ScrolledList('Physical Card Sets')
        else:
            return
        self.csFrame.set_select_single()
        self.oDlg.vbox.pack_start(self.csFrame)
        self.csFrame.set_size_request(150,300)
        for cs in oSelect:
            if cs.name != self.view.sSetName:
                iter = self.csFrame.get_list().append(None)
                self.csFrame.get_list().set(iter,0,cs.name)
        self.oDlg.connect("response", self.handleResponse)
        self.oDlg.show_all()
        return self.oDlg

    def handleResponse(self,oWidget,oResponse):
        if oResponse ==  gtk.RESPONSE_OK:
            aCardSetNames = [self.view.sSetName]
            dSelect = {}
            self.csFrame.get_selection(aCardSetNames,dSelect)
            self.compCardSets(aCardSetNames)
        self.oDlg.destroy()

    def compCardSets(self, aCardSetNames):
        (dDifferences, aCommon) = self.__getCardSetList(aCardSetNames)
        parent = self.view.getWindow()
        Results = gtk.Dialog("Card Comparison",parent,gtk.DIALOG_MODAL | \
                gtk.DIALOG_DESTROY_WITH_PARENT, \
                (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        myHBox = gtk.HBox(False,0)
        if len(aCommon)>0:
            oFrame = gtk.Frame("placeholder")
            oFrame.get_label_widget().set_markup("<span foreground = \"blue\">Common Cards</span>")
            message = ""
            for cardname,cardcount in aCommon:
                message += "<span foreground = \"green\">" + cardname + \
                        "</span> : " + str(cardcount) + "\n"
            myLabel = gtk.Label()
            myLabel.set_markup(message)
            oFrame.add(myLabel)
            myHBox.pack_start(oFrame)
        if len(dDifferences[aCardSetNames[0]])>0:
            oFrame = gtk.Frame("placeholder")
            oFrame.get_label_widget().set_markup("<span foreground = \"red\">Cards only in " + aCardSetNames[0] + "</span>")
            message = ""
            for cardname,cardcount in dDifferences[aCardSetNames[0]]:
                message += "<span foreground = \"blue\">" + cardname + "</span> : " + str(cardcount) + "\n"
            myLabel = gtk.Label()
            myLabel.set_markup(message)
            oFrame.add(myLabel)
            myHBox.pack_start(oFrame)
        if len(dDifferences[aCardSetNames[1]])>0:
            oFrame = gtk.Frame("placeholder")
            oFrame.get_label_widget().set_markup("<span foreground = \"red\">Cards only in " + aCardSetNames[1] + "</span>")
            message = ""
            for cardname,cardcount in dDifferences[aCardSetNames[1]]:
                message += "<span foreground = \"blue\">" + cardname + "</span> : " + str(cardcount) + "\n"
            myLabel = gtk.Label()
            myLabel.set_markup(message)
            oFrame.add(myLabel)
            myHBox.pack_start(oFrame)
        Results.vbox.pack_start(myHBox)
        Results.show_all()
        Results.run()
        Results.destroy()

    def __getCardSetList(self,aCardSetNames):
        dFullCardList = {}
        name1 = aCardSetNames[0]
        name2 = aCardSetNames[1]
        for name in aCardSetNames:
            if self._sModelType == AbstractCardSet.sqlmeta.table:
                oFilter = AbstractCardSetFilter(name)
                oCS = oFilter.select(AbstractCard)
            elif self._sModelType == PhysicalCardSet.sqlmeta.table:
                oFilter = PhysicalCardSetFilter(name)
                oCS = oFilter.select(PhysicalCard)
            for oC in oCS:
                oAC = IAbstractCard(oC)
                try:
                    dFullCardList[oAC.name][name] += 1
                except KeyError:
                    dFullCardList[oAC.name] = {}
                    dFullCardList[oAC.name][name1] = 0
                    dFullCardList[oAC.name][name2] = 0
                    dFullCardList[oAC.name][name] += 1
        dDifferences = { name1 : [], name2 : [] }
        aCommon = []
        for card in dFullCardList.keys():
            diff = dFullCardList[card][name1] - dFullCardList[card][name2]
            common = min(dFullCardList[card][name1],dFullCardList[card][name2])
            if diff>0:
                dDifferences[name1].append( (card,diff) )
            elif diff<0:
                dDifferences[name2].append( (card,abs(diff)) )
            if common>0:
                aCommon.append((card,common))
        return (dDifferences,aCommon)

plugin = CardSetCompare
