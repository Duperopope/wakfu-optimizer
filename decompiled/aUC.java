/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  BL
 *  Fo
 *  Ft
 *  Fu
 *  OO
 *  aUM
 *  bEm
 *  bGV
 *  com.google.common.base.Strings
 *  ffV
 *  fhC
 *  fjm
 *  gnu.trove.set.hash.THashSet
 *  org.apache.log4j.Logger
 *  org.jetbrains.annotations.NotNull
 *  org.jetbrains.annotations.Nullable
 */
import com.google.common.base.Strings;
import gnu.trove.set.hash.THashSet;
import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import org.apache.log4j.Logger;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class aUC
extends Ft {
    private static final float hlj = 100.0f;
    private static final Logger hlk = Logger.getLogger(aUC.class);
    public static final String hll = "config.properties";
    public static final String hlm = "ANMEquipmentPath";
    public static final String hln = "ANMResourcePath";
    public static final String hlo = "playerGfxPath";
    public static final String hlp = "npcGfxPath";
    public static final String hlq = "petGfxPath";
    public static final String hlr = "gfxConfigFile";
    public static final String hls = "ANMInteractiveElementPath";
    public static final String hlt = "ANMDynamicElementPath";
    public static final String hlu = "ANMIndexFile";
    public static final String hlv = "ANMGUIPath";
    public static final String hlw = "ANMPreloadFilePattern";
    public static final String hlx = "i18nPath";
    public static final String hly = "dialogsPath";
    public static final String hlz = "useXmlTheme";
    public static final String hlA = "langIconsPath";
    public static final String hlB = "worldPositionMarkerApsPath";
    public static final String hlC = "mapsPoiPath";
    public static final String hlD = "newPoiPath";
    public static final String hlE = "zaapPoiPath";
    public static final String hlF = "dragoPoiPath";
    public static final String hlG = "cannonPoiPath";
    public static final String hlH = "boatPoiPath";
    public static final String hlI = "mapsTplgCoord";
    public static final String hlJ = "mapsGfxCoord";
    public static final String hlK = "mapsGfxPath";
    public static final String hlL = "mapsLightPath";
    public static final String hlM = "mapsTopologyPath";
    public static final String hlN = "mapsEnvironmentPath";
    public static final String hlO = "mapsAmbienceDataPath";
    public static final String hlP = "worldInfoFile";
    public static final String hlQ = "ambienceBankFile";
    public static final String hlR = "gfxPath";
    public static final String hlS = "playListBankFile";
    public static final String hlT = "soundSourceFlavor";
    public static final String hlU = "useLuaAudio";
    public static final String hlV = "particlesAudioFile";
    public static final String hlW = "animatedElementsAudioFile";
    public static final String hlX = "dynamicSoundAmbianceFile";
    public static final String hlY = "sfxSoundPath";
    public static final String hlZ = "amb2DPath";
    public static final String hma = "amb3DPath";
    public static final String hmb = "musicPath";
    public static final String hmc = "voicesPath";
    public static final String hmd = "fightSoundPath";
    public static final String hme = "guiSoundPath";
    public static final String hmf = "foleysSoundPath";
    public static final String hmg = "particlesSoundPath";
    public static final String hmh = "shadersPath";
    public static final String hmi = "videosPath";
    public static final String hmj = "highLightGfxPath";
    public static final String hmk = "particlePath";
    public static final String hml = "scriptPath";
    public static final String hmm = "defaultIconPath";
    public static final String hmn = "spellsIconsPath";
    public static final String hmo = "groupDifficultyIconsPath";
    public static final String hmp = "ecosystemDifficultyIconsPath";
    public static final String hmq = "ecosystemProtectedIconPath";
    public static final String hmr = "osamodasMonsterIconPath";
    public static final String hms = "groupDifficultyChallengeIconPath";
    public static final String hmt = "companionInFightIconsPath";
    public static final String hmu = "frescoPath";
    public static final String hmv = "itemsIconsPath";
    public static final String hmw = "elementsIconsPath";
    public static final String hmx = "elementsSmallIconsPath";
    public static final String hmy = "targetEffectIconsPath";
    public static final String hmz = "areasIconsPath";
    public static final String hmA = "areasBigIconsPath";
    public static final String hmB = "statesIconsPath";
    public static final String hmC = "timePointBonusIconsPath";
    public static final String hmD = "effectAreasIconsPath";
    public static final String hmE = "breedSmallBackgroundsPath";
    public static final String hmF = "breedBigBackgroundsPath";
    public static final String hmG = "breedIconPath";
    public static final String hmH = "breedHairIconPath";
    public static final String hmI = "breedDressIconPath";
    public static final String hmJ = "breedSoloIllustrationPath";
    public static final String hmK = "breedDuoIllustrationPath";
    public static final String hmL = "popupIconPath";
    public static final String hmM = "mentorIconPath";
    public static final String hmN = "breedSmallIconPath";
    public static final String hmO = "breedBigIconPath";
    public static final String hmP = "breedHudIconPath";
    public static final String hmQ = "breedContactListIllustrationPath";
    public static final String hmR = "breedIllustrationPath";
    public static final String hmS = "breedPortraitIllustrationPath";
    public static final String hmT = "breedCircleIllustrationPath";
    public static final String hmU = "breedCharacterChoiceIllustrationPath";
    public static final String hmV = "breedCharacterSelectionIllustrationPath";
    public static final String hmW = "breedCharacterPortrait80Path";
    public static final String hmX = "breedCharacterSheetIllustrationPath";
    public static final String hmY = "breedCharacterTurnIllustrationPath";
    public static final String hmZ = "monsterIllustrationPath";
    public static final String hna = "bossIllustrationPath";
    public static final String hnb = "defaultBossIllustrationPath";
    public static final String hnc = "defaultMonsterIllustrationPath";
    public static final String hnd = "defaultSmallMonsterIllustrationPath";
    public static final String hne = "shortcutBackgroundPath";
    public static final String hnf = "skillsIconsPath";
    public static final String hng = "challengeCategoryIconsPath";
    public static final String hnh = "challengeUserTypeIconsPath";
    public static final String hni = "challengeResultQualityIconsPath";
    public static final String hnj = "compassIconsPath";
    public static final String hnk = "guildBlazonBackgroundPartPath";
    public static final String hnl = "guildBlazonForegroundPartPath";
    public static final String hnm = "guildRankIconsPath";
    public static final String hnn = "aptitudeIconsPath";
    public static final String hno = "dimensionalBagPrimaryGemPath";
    public static final String hnp = "dimensionalBagSecondaryGemPath";
    public static final String hnq = "calendarEventPath";
    public static final String hnr = "lootTypeIconsPath";
    public static final String hns = "weatherIconsPath";
    public static final String hnt = "windForceIconsPath";
    public static final String hnu = "protectorBuffsIconsPath";
    public static final String hnv = "nationFlagIconsPath";
    public static final String hnw = "nationSelectionIconsPath";
    public static final String hnx = "challengeFlyingImagePath";
    public static final String hny = "lawFlyingImagePath";
    public static final String hnz = "craftPassportIconsPath";
    public static final String hnA = "passportStampIconsPath";
    public static final String hnB = "emoteIconsPath";
    public static final String hnC = "breedEmoteIconsPath";
    public static final String hnD = "playerEmoteIconsPath";
    public static final String hnE = "emotePath";
    public static final String hnF = "monstersFamily";
    public static final String hnG = "achievementCategoryPath";
    public static final String hnH = "achievementIllustrationsPath";
    public static final String hnI = "achievementPath";
    public static final String hnJ = "titlePath";
    public static final String hnK = "currencyIconUrl";
    public static final String hnL = "backgroundDisplayPath";
    public static final String hnM = "backgroundDisplayBackgroundPath";
    public static final String hnN = "interactiveDialogPortraitPath";
    public static final String hnO = "temperatureInfluenceIconUrl";
    public static final String hnP = "protectorSecretIconUrl";
    public static final String hnQ = "effectDescPlotIconUrl";
    public static final String hnR = "giftTypeIconPath";
    public static final String hnS = "zaapTypeIconPath";
    public static final String hnT = "governmentRankIconPath";
    public static final String hnU = "itemTypeIconPath";
    public static final String hnV = "messageBoxIconsPath";
    public static final String hnW = "guildStorageTypeIconsPath";
    public static final String hnX = "antiAddictionIconsPath";
    public static final String hnY = "pvpRankIconsPath";
    public static final String hnZ = "pvpRankPassportIconsPath";
    public static final String hoa = "battlegroundTypeIcons";
    public static final String hob = "themeItemBorder";
    public static final String hoc = "themeBuildIcons";
    public static final String hod = "themeDungeonLadderCrowns";
    public static final String hoe = "themeBattlegroundStates";
    public static final String hof = "themeRolesIcon";
    public static final String hog = "themeRolesSelectIcon";
    public static final String hoh = "boosterPrivilegeIcon";
    public static final String hoi = "serverIllustrationPath";
    public static final String hoj = "serverCharacterIllustrationPath";
    public static final String hok = "serverBackgroundIllustrationPath";
    public static final String hol = "serverTilesPath";
    public static final String hom = "defaultBackgroundIllustrationPath";
    public static final String hon = "hwBuidingIconGreenPath";
    public static final String hoo = "hwBuidingIconOrangePath";
    public static final String hop = "hwBuidingIconRedPath";
    public static final String hoq = "characteristicsIconsPath";
    public static final String hor = "textIconsPath";
    public static final String hos = "activateMapParticles";
    public static final String hot = "appSkinPath";
    public static final String hou = "themeDirectory";
    public static final String hov = "themeDescriptionFolder";
    public static final String how = "tutorialFile";
    public static final String hox = "dayLightFile";
    public static final String hoy = "defaultShortcutsFile";
    public static final String hoz = "defaultChatFile";
    public static final String hoA = "defaultDayLightFile";
    public static final String hoB = "soundBankFile";
    public static final String hoC = "reverbPresetFile";
    public static final String hoD = "rollOffPresetFile";
    public static final String hoE = "lowPassPresetFile";
    public static final String hoF = "barksFile";
    public static final String hoG = "groundsFile";
    public static final String hoH = "mountsFile";
    public static final String hoI = "elementsFile";
    public static final String hoJ = "groupsFile";
    public static final String hoK = "buildingFile";
    public static final String hoL = "buildingImagePath";
    public static final String hoM = "buildingImageOffsetFile";
    public static final String hoN = "buildingMiniImagePath";
    public static final String hoO = "partitionPatchFile";
    public static final String hoP = "patchImagePath";
    public static final String hoQ = "patchImageOffsetFile";
    public static final String hoR = "patchMiniImagePath";
    public static final String hoS = "mapDefinitionPath";
    public static final String hoT = "mapScrollDecoratorPath";
    public static final String hoU = "fullSubMapPath";
    public static final String hoV = "fullMapPath";
    public static final String hoW = "completeMapPath";
    public static final String hoX = "completeMapCoordsPath";
    public static final String hoY = "miniMapPointFile";
    public static final String hoZ = "miniMapPointBigFile";
    public static final String hpa = "compassPointFile";
    public static final String hpb = "fightChallengeIconsPath";
    public static final String hpc = "pointsOfInterestIconPath";
    public static final String hpd = "pointsOfInterestDefaultSmallIconPath";
    public static final String hpe = "pointsOfInterestProtectorIconPath";
    public static final String hpf = "pointsOfInterestProtectorinChaosIconPath";
    public static final String hpg = "partyMemberPoiPath";
    public static final String hph = "highLightGfxDefaultFile";
    public static final String hpi = "contentStaticDataStorageDirectory";
    public static final String hpj = "binaryDataFile";
    public static final String hpk = "merchantDisplayIconPath";
    public static final String hpl = "pictoIconPath";
    public static final String hpm = "imagesPath";
    public static final String hpn = "soundDevice";
    public static final String hpo = "soundEnable";
    public static final String hpp = "soundAmbianceEnable";
    public static final String hpq = "amb2DMix";
    public static final String hpr = "amb3DMix";
    public static final String hps = "guiMix";
    public static final String hpt = "musicMix";
    public static final String hpu = "sfxMix";
    public static final String hpv = "fightsMix";
    public static final String hpw = "voicesMix";
    public static final String hpx = "foleysMix";
    public static final String hpy = "particlesMix";
    private static final String hpz = "dynamicSpellMixFadeOut";
    private static final String hpA = "dynamicSpellMix";
    public static final String hpB = "connectionRetryCount";
    public static final String hpC = "connectionRetryDelay";
    public static final String hpD = "dispatchAddresses";
    public static final String hpE = "bugReport.enable";
    public static final String hpF = "bugReport.url";
    public static final String hpG = "linkSteamAccountUrl";
    public static final String hpH = "accountCreationUrl";
    public static final String hpI = "forgottenPasswordUrl";
    public static final String hpJ = "accountValidationUrl";
    public static final String hpK = "antiAddictionAccountCheckURL";
    public static final String hpL = "cacheDirectory";
    public static final String hpM = "autoLogin";
    public static final String hpN = "autoLogin_login";
    public static final String hpO = "autoLogin_password";
    public static final String hpP = "autoLogin_selectCharacter";
    public static final String hpQ = "autopassword";
    public static final String hpR = "climateBonusIconsPath";
    public static final String hpS = "worldMapAnmFilePath";
    public static final String hpT = "bannerAnmFilePath";
    public static final String hpU = "bannerImageFilePath";
    public static final String hpV = "bannerImageLocalizedFilePath";
    public static final String hpW = "fightBannerAnmFilePath";
    public static final String hpX = "compassTypePath";
    public static final String hpY = "dialogChoiceTypePath";
    public static final String hpZ = "rewardTypeIconsPath";
    public static final String hqa = "language.force";
    public static final String hqb = "shopBuyOgrinesUrl";
    public static final String hqc = "shopServices";
    public static final String hqd = "haapiAnkamaUrl";
    public static final String hqe = "haapiWakfuUrl";
    public static final String hqf = "shopiUrl";
    public static final String hqg = "interChatUrl";
    public static final String hqh = "tutorialIconsPath";
    public static final String hqi = "guideIconsPath";
    public static final String hqj = "guideIllustrationsPath";
    public static final String hqk = "guideIllustrationsLocalizedFilePath";
    public static final String hql = "nationLawsIconsPath";
    public static final String hqm = "characterCreation.tuto.force";
    public static final String hqn = "resolution.min.width";
    public static final String hqo = "resolution.min.height";
    public static final String hqp = "enableRandomCharacterName";
    public static final String hqq = "activateStuffPreview";
    public static final String hqr = "companionCharacterSheetIllustrationPath";
    public static final String hqs = "companionBigCharacterSheetIllustrationPath";
    public static final String hqt = "companionIconsPath";
    public static final String hqu = "companionListIllustrationsPath";
    public static final String hqv = "companionSpellInventoryIllustrationsPath";
    public static final String hqw = "companionCircleIllustrationPath";
    public static final String hqx = "companionTurnIllustrationPath";
    public static final String hqy = "UPDATER_COMMUNICATION_PORT";
    public static final String hqz = "UPDATER_INITIAL_STATE";
    public static final String hqA = "cgvUrl";
    public static final String hqB = "payementHandleUrl";
    public static final String hqC = "payementOgrinesHandleUrl";
    public static final String hqD = "branch";
    public static final String hqE = "loadAchievements";
    public static final String hqF = "loadGameEvents";
    public static final String hqG = "dontAskForTuto";
    public static final String hqH = "disableCharacterManagement";
    public static final String hqI = "disableTacticalView";
    public static final String hqJ = "useLuaCache";
    public static final String hqK = "onStartupClientBenchmark";
    public static final String hqL = "onStartupClientHardwareTest";
    public static final String hqM = "gameRequirements.url";
    public static final String hqN = "displayDisconnectButton";
    public static final String hqO = "defaultProvidedTheme";
    public static final String hqP = "nameForced";
    private static final aUC hqQ = new aUC();
    public static final String hqR = ".xps";
    private final THashSet<String> hqS = new THashSet();

    public static aUC cVq() {
        return hqQ;
    }

    public String cVr() {
        return this.l(hly, "");
    }

    public boolean cVs() {
        return this.bZ("");
    }

    public boolean bZ(String string) {
        hlk.info((Object)String.format("Chargement de la configuration depuis le fichier : '%s'", string));
        return super.bZ(Strings.isNullOrEmpty((String)string) ? hll : string);
    }

    public float cVt() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpx, 100.0f) / 100.0f));
    }

    public float cVu() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpy, 100.0f) / 100.0f));
    }

    public float cVv() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpu, 100.0f) / 100.0f));
    }

    public float cVw() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpq, 100.0f) / 100.0f));
    }

    public float cVx() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpr, 100.0f) / 100.0f));
    }

    public float cVy() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpv, 100.0f) / 100.0f));
    }

    public float cVz() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hps, 100.0f) / 100.0f));
    }

    public float cVA() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpt, 100.0f) / 100.0f));
    }

    public float cVB() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpw, 100.0f) / 100.0f));
    }

    public float cVC() {
        return this.a(hpz, 1.0f);
    }

    public float cVD() {
        return Math.min(1.0f, Math.max(0.0f, this.a(hpA, 100.0f) / 100.0f));
    }

    @Nullable
    public String zt(int n) {
        try {
            return this.bS(hmk) + n + hqR;
        }
        catch (Fu fu) {
            hlk.warn((Object)fu);
            return null;
        }
    }

    @Nullable
    public String a(String string, String string2, Object ... objectArray) {
        try {
            String string3 = Fo.b((String)this.bS(string), (Object[])objectArray);
            if (string3 != null && BL.bl((String)string3)) {
                return string3;
            }
            if (!this.hqS.contains((Object)string3)) {
                hlk.warn((Object)("Impossible de trouver l'icone d'URL " + string3));
                this.hqS.add((Object)string3);
            }
            if (string2 != null) {
                return aUC.kG(string2);
            }
            return null;
        }
        catch (Fu fu) {
            hlk.warn((Object)fu.getMessage());
            return null;
        }
    }

    public boolean h(String string, Object ... objectArray) {
        try {
            String string2 = Fo.b((String)this.bS(string), (Object[])objectArray);
            return string2 != null && BL.bl((String)string2);
        }
        catch (Fu fu) {
            hlk.warn((Object)("Unable to read icon with key " + string + " and args " + Arrays.toString(objectArray)), (Throwable)fu);
            return false;
        }
    }

    public boolean zu(int n) {
        return this.h(hmZ, n);
    }

    public String zv(int n) {
        return this.a(hmZ, hnc, n);
    }

    public String zw(int n) {
        return this.a(hna, hnb, n);
    }

    public String dd(int n, int n2) {
        try {
            return String.format(aUC.cVq().bS(hmV), n, n2);
        }
        catch (Fu fu) {
            return null;
        }
    }

    public String a(@Nullable fjm fjm2, int n) {
        bGV bGV2 = (bGV)bEm.dSb().Vd(n);
        if (bGV2 == null) {
            hlk.warn((Object)("Unable to retrieve reference item with following id : " + n + " (We return a default icon instead)"), (Throwable)new NullPointerException());
            return aUC.cVE();
        }
        return this.a(fjm2, (fhC)bGV2);
    }

    public String a(@Nullable fjm fjm2, @NotNull ffV ffV2) {
        if (fjm2 == null) {
            hlk.warn((Object)"Unable to fetch sex from a null citizen, we use default gfxId of item instead", (Throwable)new NullPointerException());
            return this.zx(ffV2.aVt());
        }
        return this.zx(fjm2.aWO() == 1 ? ffV2.cpf() : ffV2.aVt());
    }

    public String a(@Nullable fjm fjm2, @NotNull fhC fhC2) {
        if (fjm2 == null) {
            hlk.warn((Object)"Unable to fetch sex from a null citizen, we use default gfxId of item instead", (Throwable)new NullPointerException());
            return this.zx(fhC2.aVt());
        }
        return this.zx(fjm2.aWO() == 1 ? fhC2.cpf() : fhC2.aVt());
    }

    public String zx(int n) {
        return this.a(hmv, hmm, n);
    }

    public static String cVE() {
        try {
            return aUC.kG(hmm);
        }
        catch (Fu fu) {
            hlk.warn((Object)"Could not find default icon at path defaultIconPath", (Throwable)fu);
            return null;
        }
    }

    public boolean zy(int n) {
        return this.h(hmv, n);
    }

    public String zz(int n) {
        return this.a(hmv, hmm, n);
    }

    public String zA(int n) {
        return this.a(hmn, hmm, n);
    }

    public String zB(int n) {
        return this.a(hmn, hmm, n);
    }

    public String zC(int n) {
        return this.a(hnf, hmm, "c" + n);
    }

    public String zD(int n) {
        return this.zC(n);
    }

    public String zE(int n) {
        return this.a(hnf, hmm, n);
    }

    public String zF(int n) {
        return this.a(hnn, hmm, n);
    }

    public String aY(byte by) {
        return this.a(hnq, hmm, by);
    }

    public String zG(int n) {
        return this.a(hnv, hmm, n);
    }

    public String zH(int n) {
        return this.a(hnw, hmm, n);
    }

    public String zI(int n) {
        return this.a(hpY, hmm, n);
    }

    public String zJ(int n) {
        return this.a(hnB, null, n);
    }

    public String zK(int n) {
        return this.a(hnC, null, n);
    }

    public String kt(String string) {
        return this.a(hnD, null, string);
    }

    public String ku(String string) {
        return this.a(hob, null, string);
    }

    public String kv(String string) {
        return this.a(hoc, null, string);
    }

    public String kw(String string) {
        return this.a(hoa, null, string);
    }

    public String kx(String string) {
        return this.a(hof, null, string);
    }

    public String cVF() {
        return this.a(hog, null, new Object[0]);
    }

    public String ky(String string) {
        return this.a(hod, null, string);
    }

    public String kz(String string) {
        return this.a(hoe, null, string);
    }

    public static String kA(String string) {
        return "laurels" + string;
    }

    public String zL(int n) {
        return this.a(hnE, null, n);
    }

    public String zM(int n) {
        return this.a(hnG, null, n);
    }

    public String kB(String string) {
        return this.a(hnH, null, string);
    }

    public String zN(int n) {
        return this.a(hnI, null, n);
    }

    public String zO(int n) {
        return this.a(hnJ, null, new Object[0]);
    }

    public String zP(int n) {
        return this.a(hnL, null, n);
    }

    public String zQ(int n) {
        return this.a(hnM, null, n);
    }

    public String kC(String string) {
        return this.a(hnN, null, string);
    }

    public String kD(String string) {
        return this.a(hqh, null, string);
    }

    public String zR(int n) {
        return this.a(hqi, null, n);
    }

    public String kE(String string) {
        String string2 = this.a(hqk, null, string, aUM.cWf().aUXX().aUP());
        if (BL.bl((String)string2)) {
            return string2;
        }
        return this.a(hqj, null, string);
    }

    public String ix(long l) {
        return this.a(hql, null, l);
    }

    public String aZ(short s) {
        return this.a(hnU, null, s);
    }

    public String de(int n, int n2) {
        return this.a(hoh, null, n, n2);
    }

    @Nullable
    public String cVG() {
        try {
            return String.format(this.bS(hqM), aUM.cWf().aUXX().aUS());
        }
        catch (Fu fu) {
            hlk.error((Object)"Unable to retrieve url of game requirements.", (Throwable)fu);
            return null;
        }
    }

    public String kF(String string) {
        String string2;
        try {
            string2 = this.bS(hpL) + File.separatorChar + string;
        }
        catch (Fu fu) {
            string2 = "./cache/" + string;
        }
        return string2;
    }

    public static String kG(String string) {
        return Fo.bB((String)aUC.cVq().bS(string));
    }

    public static String i(String string, Object ... objectArray) {
        String string2 = String.format(aUC.cVq().bS(string), objectArray);
        return Fo.bB((String)string2);
    }

    public boolean cVH() {
        String string = this.l(hqz, null);
        return "uptodate".equalsIgnoreCase(string);
    }

    public ArrayList<OO> cVI() {
        ArrayList<OO> arrayList = new ArrayList<OO>();
        try {
            String string = this.bS(hpD);
            String[] stringArray = string.split(":");
            if (stringArray.length == 2) {
                String string2 = stringArray[0];
                String[] stringArray2 = stringArray[1].split(";");
                for (int i = 0; i < stringArray2.length; ++i) {
                    arrayList.add(new OO(string2, Integer.parseInt(stringArray2[i])));
                }
            }
        }
        catch (Fu fu) {
            hlk.error((Object)"PropertyException during getDispatchAddresses", (Throwable)fu);
        }
        return arrayList;
    }
}
