# SutekhObjects.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2005, 2006, 2007 Simon Cross <hodgestar@gmail.com>
# Copyright 2006, 2007 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details

"""The database definitions and pyprotocols adaptors for Sutekh"""

from sutekh.core.CachedRelatedJoin import CachedRelatedJoin, \
        SOCachedRelatedJoin
from sutekh.core.Abbreviations import CardTypes, Clans, Creeds, Disciplines, \
        Expansions, Rarities, Sects, Titles, Virtues
# pylint: disable-msg=E0611
# pylint doesn't parse sqlobject's column declaration magic correctly
from sqlobject import sqlmeta, SQLObject, IntCol, UnicodeCol, RelatedJoin, \
       EnumCol, MultipleJoin, BoolCol, DatabaseIndex, ForeignKey, \
       SQLObjectNotFound
# pylint: enable-msg=E0611
from protocols import advise, Interface

# Interfaces

# pylint: disable-msg=R0923, C0111, C0321
# R0923 - PyProtocols magic will take care of the implementation
# C0111 - No point in docstrings for these classes, really
# C0321 - Compactness of single line definitions is good here

class IAbstractCard(Interface): pass
class IPhysicalCard(Interface): pass
class IAbstractCardSet(Interface): pass
class IPhysicalCardSet(Interface): pass
class IRarityPair(Interface): pass
class IExpansion(Interface): pass
class IRarity(Interface): pass
class IDisciplinePair(Interface): pass
class IDiscipline(Interface): pass
class IClan(Interface): pass
class ICardType(Interface): pass
class ISect(Interface): pass
class ITitle(Interface): pass
class ICreed(Interface): pass
class IVirtue(Interface): pass
class IRuling(Interface): pass

# pylint: enable-msg=R0923, C0111, C0321
# Table Objects

# pylint: disable-msg=W0232
# Most of the classes defined here don't have __init__ methods by design

class VersionTable(SQLObject):
    TableName = UnicodeCol(alternateID=True, length=50)
    Version = IntCol(default=None)
    tableversion = 1

class AbstractCard(SQLObject):
    advise(instancesProvide=[IAbstractCard])

    tableversion = 3
    sqlmeta.lazyUpdate = True

    canonicalName = UnicodeCol(alternateID=True, length=50)
    name = UnicodeCol(length=50)
    text = UnicodeCol()
    group = IntCol(default=None, dbName='grp')
    capacity = IntCol(default=None)
    cost = IntCol(default=None)
    life = IntCol(default=None)
    costtype = EnumCol(enumValues=['pool', 'blood', 'conviction', None],
            default=None)
    level = EnumCol(enumValues=['advanced', None], default=None)
    burnoption = BoolCol(default=False)

    discipline = CachedRelatedJoin('DisciplinePair',
            intermediateTable='abs_discipline_pair_map',
            createRelatedTable=False)
    rarity = CachedRelatedJoin('RarityPair',
            intermediateTable='abs_rarity_pair_map',
            createRelatedTable=False)
    clan = CachedRelatedJoin('Clan',
            intermediateTable='abs_clan_map', createRelatedTable=False)
    cardtype = CachedRelatedJoin('CardType', intermediateTable='abs_type_map',
            createRelatedTable=False)
    sect = CachedRelatedJoin('Sect', intermediateTable='abs_sect_map',
            createRelatedTable=False)
    title = CachedRelatedJoin('Title', intermediateTable='abs_title_map',
            createRelatedTable=False)
    creed = CachedRelatedJoin('Creed', intermediateTable='abs_creed_map',
            createRelatedTable=False)
    virtue = CachedRelatedJoin('Virtue', intermediateTable='abs_virtue_map',
            createRelatedTable=False)
    rulings = CachedRelatedJoin('Ruling', intermediateTable='abs_ruling_map',
            createRelatedTable=False)

    sets = RelatedJoin('AbstractCardSet', intermediateTable='abstract_map',
            createRelatedTable=False)
    physicalCards = MultipleJoin('PhysicalCard')

class PhysicalCard(SQLObject):
    advise(instancesProvide=[IPhysicalCard])

    tableversion = 2
    abstractCard = ForeignKey('AbstractCard')
    abstractCardIndex = DatabaseIndex(abstractCard)
    # Explicitly allow None as expansion
    expansion = ForeignKey('Expansion', notNull=False)
    sets = RelatedJoin('PhysicalCardSet', intermediateTable='physical_map',
            createRelatedTable=False)

class AbstractCardSet(SQLObject):
    advise(instancesProvide=[IAbstractCardSet])

    tableversion = 3
    name = UnicodeCol(alternateID=True, length=50)
    author = UnicodeCol(length=50, default='')
    comment = UnicodeCol(default='')
    annotations = UnicodeCol(default='')
    cards = RelatedJoin('AbstractCard', intermediateTable='abstract_map',
            createRelatedTable=False)

class PhysicalCardSet(SQLObject):
    advise(instancesProvide=[IPhysicalCardSet])

    tableversion = 4
    name = UnicodeCol(alternateID=True, length=50)
    author = UnicodeCol(length=50, default='')
    comment = UnicodeCol(default='')
    annotations = UnicodeCol(default='')
    inuse = BoolCol(default=False)
    cards = RelatedJoin('PhysicalCard', intermediateTable='physical_map',
            createRelatedTable=False)

class RarityPair(SQLObject):
    advise(instancesProvide=[IRarityPair])

    tableversion = 1
    expansion = ForeignKey('Expansion')
    rarity = ForeignKey('Rarity')
    cards = RelatedJoin('AbstractCard',
            intermediateTable='abs_rarity_pair_map', createRelatedTable=False)
    expansionRarityIndex = DatabaseIndex(expansion, rarity, unique=True)

class Expansion(SQLObject):
    advise(instancesProvide=[IExpansion])

    tableversion = 2
    name = UnicodeCol(alternateID=True, length=20)
    shortname = UnicodeCol(length=10, default=None)
    pairs = MultipleJoin('RarityPair')

class Rarity(SQLObject):
    advise(instancesProvide=[IRarity])

    tableversion = 2
    name = UnicodeCol(alternateID=True, length=20)
    shortname = UnicodeCol(alternateID=True, length=20)

class DisciplinePair(SQLObject):
    advise(instancesProvide=[IDisciplinePair])

    tableversion = 1
    discipline = ForeignKey('Discipline')
    level = EnumCol(enumValues=['inferior', 'superior'])
    disciplineLevelIndex = DatabaseIndex(discipline, level, unique=True)
    cards = RelatedJoin('AbstractCard',
            intermediateTable='abs_discipline_pair_map',
            createRelatedTable=False)

class Discipline(SQLObject):
    advise(instancesProvide=[IDiscipline])

    tableversion = 2
    name = UnicodeCol(alternateID=True, length=30)
    fullname = UnicodeCol(length=30, default=None)
    pairs = MultipleJoin('DisciplinePair')

class Virtue(SQLObject):
    advise(instancesProvide=[IVirtue])

    tableversion = 1
    name = UnicodeCol(alternateID=True, length=30)
    fullname = UnicodeCol(length=30, default=None)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_virtue_map',
            createRelatedTable=False)

class Creed(SQLObject):
    advise(instancesProvide=[ICreed])

    tableversion = 1
    name = UnicodeCol(alternateID=True, length=40)
    shortname = UnicodeCol(length=10, default=None)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_creed_map',
            createRelatedTable=False)

class Clan(SQLObject):
    advise(instancesProvide=[IClan])

    tableversion = 2
    name = UnicodeCol(alternateID=True, length=40)
    shortname = UnicodeCol(length=10, default=None)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_clan_map',
            createRelatedTable=False)

class CardType(SQLObject):
    advise(instancesProvide=[ICardType])

    tableversion = 1
    name = UnicodeCol(alternateID=True, length=50)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_type_map',
            createRelatedTable=False)

class Sect(SQLObject):
    advise(instancesProvide=[ISect])

    tableversion = 1
    name = UnicodeCol(alternateID=True, length=50)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_sect_map',
            createRelatedTable=False)

class Title(SQLObject):
    advise(instancesProvide=[ITitle])

    tableversion = 1
    name = UnicodeCol(alternateID=True, length=50)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_title_map',
            createRelatedTable=False)

class Ruling(SQLObject):
    advise(instancesProvide=[IRuling])

    tableversion = 1
    text = UnicodeCol(alternateID=True, length=512)
    code = UnicodeCol(length=50)
    url = UnicodeCol(length=256, default=None)
    cards = RelatedJoin('AbstractCard', intermediateTable='abs_ruling_map',
            createRelatedTable=False)

# Mapping Tables

class MapPhysicalCardToPhysicalCardSet(SQLObject):
    class sqlmeta:
        table = 'physical_map'

    tableversion = 1

    physicalCard = ForeignKey('PhysicalCard', notNull=True)
    physicalCardSet = ForeignKey('PhysicalCardSet', notNull=True)

    physicalCardIndex = DatabaseIndex(physicalCard, unique=False)
    physicalCardSetIndex = DatabaseIndex(physicalCardSet, unique=False)
    jointIndex = DatabaseIndex(physicalCard, physicalCardSet, unique=False)

class MapAbstractCardToAbstractCardSet(SQLObject):
    class sqlmeta:
        table = 'abstract_map'

    tableversion = 1
    abstractCard = ForeignKey('AbstractCard', notNull=True)
    abstractCardSet = ForeignKey('AbstractCardSet', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    abstractCardSetIndex = DatabaseIndex(abstractCardSet, unique=False)

class MapAbstractCardToRarityPair(SQLObject):
    class sqlmeta:
        table = 'abs_rarity_pair_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    rarityPair = ForeignKey('RarityPair', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    rarityPairIndex = DatabaseIndex(rarityPair, unique=False)

class MapAbstractCardToRuling(SQLObject):
    class sqlmeta:
        table = 'abs_ruling_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    ruling = ForeignKey('Ruling', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    rulingIndex = DatabaseIndex(ruling, unique=False)

class MapAbstractCardToClan(SQLObject):
    class sqlmeta:
        table = 'abs_clan_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    clan = ForeignKey('Clan', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    clanIndex = DatabaseIndex(clan, unique=False)

class MapAbstractCardToDisciplinePair(SQLObject):
    class sqlmeta:
        table = 'abs_discipline_pair_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    disciplinePair = ForeignKey('DisciplinePair', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    disciplinePairIndex = DatabaseIndex(disciplinePair, unique=False)

class MapAbstractCardToCardType(SQLObject):
    class sqlmeta:
        table = 'abs_type_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    cardType = ForeignKey('CardType', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    cardTypeIndex = DatabaseIndex(cardType, unique=False)

class MapAbstractCardToSect(SQLObject):
    class sqlmeta:
        table = 'abs_sect_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    sect = ForeignKey('Sect', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    sectIndex = DatabaseIndex(sect, unique=False)

class MapAbstractCardToTitle(SQLObject):
    class sqlmeta:
        table = 'abs_title_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    title = ForeignKey('Title', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    titleIndex = DatabaseIndex(title, unique=False)

class MapAbstractCardToCreed(SQLObject):
    class sqlmeta:
        table = 'abs_creed_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    creed = ForeignKey('Creed', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    creedIndex = DatabaseIndex(creed, unique=False)

class MapAbstractCardToVirtue(SQLObject):
    class sqlmeta:
        table = 'abs_virtue_map'

    tableversion = 1

    abstractCard = ForeignKey('AbstractCard', notNull=True)
    virtue = ForeignKey('Virtue', notNull=True)

    abstractCardIndex = DatabaseIndex(abstractCard, unique=False)
    virtueIndex = DatabaseIndex(virtue, unique=False)

# List of Tables to be created, dropped, etc.

ObjectList = [ AbstractCard, Expansion,
               PhysicalCard, AbstractCardSet, PhysicalCardSet,
               Rarity, RarityPair, Discipline, DisciplinePair,
               Clan, CardType, Sect, Title, Ruling, Virtue, Creed,
               # Mapping tables from here on out
               MapPhysicalCardToPhysicalCardSet,
               MapAbstractCardToAbstractCardSet,
               MapAbstractCardToRarityPair,
               MapAbstractCardToRuling,
               MapAbstractCardToClan,
               MapAbstractCardToDisciplinePair,
               MapAbstractCardToCardType,
               MapAbstractCardToSect,
               MapAbstractCardToTitle,
               MapAbstractCardToVirtue,
               MapAbstractCardToCreed,
               ]

PhysicalList = [PhysicalCard, PhysicalCardSet,
        MapPhysicalCardToPhysicalCardSet]
AbstractCardSetList = [AbstractCardSet, MapAbstractCardToAbstractCardSet]

# Object Maker API

class SutekhObjectMaker(object):
    """Creates all kinds of SutekhObjects from simple strings.

       All the methods will return either a copy of an existing object
       or a new object.
       """
    def _make_object(self, cObjClass, cInterface, cAbbreviation, sObj,
            bShortname=False, bFullname=False):
        try:
            return cInterface(sObj)
        except SQLObjectNotFound:
            sObj = cAbbreviation.canonical(sObj)
            dKw = { 'name': sObj }
            if bShortname:
                dKw['shortname'] = cAbbreviation.shortname(sObj)
            if bFullname:
                dKw['fullname'] = cAbbreviation.fullname(sObj)
            return cObjClass(**dKw)

    def makeCardType(self, sType):
        return self._make_object(CardType, ICardType, CardTypes, sType)

    def makeClan(self, sClan):
        return self._make_object(Clan, IClan, Clans, sClan, bShortname=True)

    def makeCreed(self, sCreed):
        return self._make_object(Creed, ICreed, Creeds, sCreed,
                bShortname=True)

    def makeDiscipline(self, sDis):
        return self._make_object(Discipline, IDiscipline, Disciplines, sDis,
                bFullname=True)

    def makeExpansion(self, sExpansion):
        return self._make_object(Expansion, IExpansion, Expansions, sExpansion,
                bShortname=True)

    def makeRarity(self, sRarity):
        return self._make_object(Rarity, IRarity, Rarities, sRarity,
                bShortname=True)

    def makeSect(self, sSect):
        return self._make_object(Sect, ISect, Sects, sSect)

    def makeTitle(self, sTitle):
        return self._make_object(Title, ITitle, Titles, sTitle)

    def makeVirtue(self, sVirtue):
        return self._make_object(Virtue, IVirtue, Virtues, sVirtue,
                bFullname=True)

    def makeAbstractCard(self, sCard):
        try:
            return IAbstractCard(sCard)
        except SQLObjectNotFound:
            sName = sCard.strip()
            sCanonical = sName.lower()
            return AbstractCard(canonicalName=sCanonical, name=sName, text="")

    def makeRarityPair(self, sExp, sRarity):
        try:
            return IRarityPair((sExp, sRarity))
        except SQLObjectNotFound:
            oExp = self.makeExpansion(sExp)
            oRarity = self.makeRarity(sRarity)
            return RarityPair(expansion=oExp, rarity=oRarity)

    def makeDisciplinePair(self, sDiscipline, sLevel):
        try:
            return IDisciplinePair((sDiscipline, sLevel))
        except SQLObjectNotFound:
            oDis = self.makeDiscipline(sDiscipline)
            return DisciplinePair(discipline=oDis, level=sLevel)

    def makeRuling(self, sText, sCode):
        try:
            return IRuling((sText, sCode))
        except SQLObjectNotFound:
            return Ruling(text=sText, code=sCode)

# Abbreviation lookup based adapters

class StrAdaptMeta(type):
    def __init__(self, sName, aBases, dDict):
        self.make_object_cache()

    def make_object_cache(self):
        self.__dCache = {}

    def fetch(self, sName, oCls):
        oObj = self.__dCache.get(sName, None)
        if oObj is None:
            oObj = oCls.byName(sName.encode('utf8'))
            self.__dCache[sName] = oObj

        return oObj

class CardTypeAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[ICardType], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(CardTypes.canonical(sName), CardType)

class ClanAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[IClan], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Clans.canonical(sName), Clan)

class CreedAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[ICreed], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Creeds.canonical(sName), Creed)

class DisciplineAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[IDiscipline], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Disciplines.canonical(sName), Discipline)

class ExpansionAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[IExpansion], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Expansions.canonical(sName), Expansion)

class RarityAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[IRarity], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Rarities.canonical(sName), Rarity)

class SectAdaptor(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[ISect], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Sects.canonical(sName), Sect)

class TitleAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[ITitle], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Titles.canonical(sName), Title)

class VirtueAdapter(object):
    # pylint: disable-msg=E1101
    # metaclass confuses pylint
    __metaclass__ = StrAdaptMeta
    advise(instancesProvide=[IVirtue], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        return cls.fetch(Virtues.canonical(sName), Virtue)

# Other Adapters

class RarityPairAdapter(object):
    advise(instancesProvide=[IRarityPair], asAdapterForTypes=[tuple])

    __dCache = {}

    @classmethod
    def make_object_cache(cls):
        cls.__dCache = {}

    def __new__(cls, tData):
        # pylint: disable-msg=E1101
        # adaptors confuses pylint
        oExp = IExpansion(tData[0])
        oRarity = IRarity(tData[1])

        oPair = cls.__dCache.get((oExp.id, oRarity.id), None)
        if oPair is None:
            oPair = RarityPair.selectBy(expansion=oExp,
                    rarity=oRarity).getOne()
            cls.__dCache[(oExp.id, oRarity.id)] = oPair

        return oPair

class DisciplinePairAdapter(object):
    advise(instancesProvide=[IDisciplinePair], asAdapterForTypes=[tuple])

    __dCache = {}

    @classmethod
    def make_object_cache(cls):
        cls.__dCache = {}

    def __new__(cls, tData):
        # pylint: disable-msg=E1101
        # adaptors confuses pylint
        oDis = IDiscipline(tData[0])
        sLevel = str(tData[1])

        oPair = cls.__dCache.get((oDis.id, sLevel), None)
        if oPair is None:
            oPair = DisciplinePair.selectBy(discipline=oDis,
                    level=sLevel).getOne()
            cls.__dCache[(oDis.id, sLevel)] = oPair

        return oPair

class AbstractCardAdapter(object):
    advise(instancesProvide=[IAbstractCard], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        # pylint: disable-msg=E1101
        # SQLObject confuses pylint
        return AbstractCard.byCanonicalName(sName.encode('utf8').lower())

class RulingAdapter(object):
    advise(instancesProvide=[IRuling], asAdapterForTypes=[tuple])

    def __new__(cls, tData):
        # pylint: disable-msg=E1101
        # SQLObject confuses pylint
        sText, sCode = tData
        return Ruling.byText(sText.encode('utf8'))

class AbstractCardSetAdapter(object):
    advise(instancesProvide=[IAbstractCardSet], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        # pylint: disable-msg=E1101
        # SQLObject confuses pylint
        return AbstractCardSet.byName(sName.encode('utf8'))

class PhysicalCardSetAdapter(object):
    advise(instancesProvide=[IPhysicalCardSet], asAdapterForTypes=[basestring])

    def __new__(cls, sName):
        # pylint: disable-msg=E1101
        # SQLObject confuses pylint
        return PhysicalCardSet.byName(sName.encode('utf8'))

class PhysicalCardToAbstractCardAdapter(object):
    advise(instancesProvide=[IAbstractCard], asAdapterForTypes=[PhysicalCard])

    def __new__(cls, oPhysCard):
        return oPhysCard.abstractCard

class MapAbstractCardToAbstractCardSetToAbstractCardAdapter(object):
    advise(instancesProvide=[IAbstractCard],
            asAdapterForTypes=[MapAbstractCardToAbstractCardSet])

    def __new__(cls, oAbstractMapEntry):
        return oAbstractMapEntry.abstractCard

# Flushing

def flush_cache():
    # Flush all the object caches - needed before importing new card lists
    # and such
    for cAdaptor in [ ExpansionAdapter, RarityAdapter, DisciplineAdapter,
                      ClanAdapter, CardTypeAdapter, SectAdaptor, TitleAdapter,
                      VirtueAdapter, CreedAdapter, DisciplinePairAdapter,
                      RarityPairAdapter ]:
        cAdaptor.make_object_cache()

    for oJoin in AbstractCard.sqlmeta.joins:
        if type(oJoin) is SOCachedRelatedJoin:
            oJoin.flush_cache()

def init_cache():
    for oJoin in AbstractCard.sqlmeta.joins:
        if type(oJoin) is SOCachedRelatedJoin:
            oJoin.init_cache()
