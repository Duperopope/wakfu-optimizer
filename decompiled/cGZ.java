/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  Bw
 *  GC
 *  MH
 *  QQ
 *  Qk
 *  aAM
 *  aAW
 *  aEF
 *  aHR
 *  aUE
 *  aUM
 *  bMB
 *  bMD
 *  bMQ
 *  bMf
 *  bMi
 *  bMt
 *  bMx
 *  bgO
 *  bgT
 *  cDU
 *  cHa
 *  cHb
 *  cHc
 *  cHd
 *  cVu
 *  cYq
 *  dbk
 *  dbo
 *  eMt
 *  eNe
 *  eNf
 *  eNh
 *  eNk
 *  eSS
 *  eTo
 *  exP
 *  fAW
 *  fBJ
 *  fDh
 *  fDu
 *  fDy
 *  fEs
 *  fGB
 *  fGC
 *  fGK
 *  fGL
 *  fGM
 *  fHs
 *  fIq
 *  fIs
 *  fLG
 *  fLV
 *  fLW
 *  fRX
 *  fSe
 *  fqX
 *  fzQ
 *  org.jetbrains.annotations.Nullable
 */
import org.jetbrains.annotations.Nullable;

@fyF
public class cGZ {
    public static final String PACKAGE = "wakfu.spellDetails";
    static int mZg = -1;

    public static void setSpellLevel(fIq fIq2) {
        if (fIq2 instanceof fLW) {
            fHs fHs2;
            short s = (short)((fLW)fIq2).getValue();
            if (s > MH.aWP.aVe()) {
                s = MH.aWP.aVe();
            }
            if ((fHs2 = fIq2.gBE().getElementMap()) == null) {
                return;
            }
            cGZ.b(s, fHs2);
        }
    }

    public static void keyType(fIq fIq2, fDu fDu2) {
        fHs fHs2;
        if (fDu2.getText().length() == 0) {
            return;
        }
        short s = Bw.r((Object)fDu2.getText());
        if (s > MH.aWP.aVe()) {
            s = MH.aWP.aVe();
        }
        if ((fHs2 = fIq2.gBE().getElementMap()) == null) {
            return;
        }
        cGZ.b(s, fHs2);
    }

    public static void processText(fIq fIq2, fEs fEs2, fRX fRX2) {
        cGZ.processText(fIq2, fEs2, fRX2, null);
    }

    public static void processText(fIq fIq2, fEs fEs2, fRX fRX2, @Nullable fRX fRX3) {
        String string;
        String string2;
        String[] stringArray;
        String string3;
        fGK fGK2;
        fDy fDy2 = (fDy)fIq2.gBE();
        fGB fGB2 = fDy2.getBlockUnderMouse();
        if (fGB2 != null && fGB2.gyV() == fGC.uuh) {
            fGK2 = fGB2.gyW();
            if (fGK2 == null) {
                return;
            }
            if (fGK2.gzE() == aHR.dSC && (string3 = ((fGM)fGK2).getId()) != null && string3.length() > 0 && (stringArray = string3.split("_")).length == 2) {
                string2 = stringArray[0];
                string = stringArray[1];
                if (string2 == null || string2.length() == 0) {
                    return;
                }
                if (string2.equals("state")) {
                    var11_11 = Integer.parseInt(string);
                    short s = GC.mS((int)var11_11);
                    short s2 = GC.mT((int)var11_11);
                    bMQ bMQ2 = (bMQ)fqX.gjM().Zr((int)s);
                    if (bMQ2.cmL() != s2) {
                        bMQ2 = bMQ2.cl(s2);
                    }
                    if (fIq2.gBy() == fzQ.tJU) {
                        bMx bMx2;
                        fHs fHs2;
                        dbo dbo2 = new dbo();
                        dbo2.b(bMQ2);
                        fHs fHs3 = fHs2 = fEs2.getElementMap().getId() == null ? fEs2.getElementMap().gAv() : fEs2.getElementMap();
                        if (fHs2 != null && (bMx2 = (bMx)fSe.gFu().aW("editableDescribedSpell", fHs2.getId())) != null) {
                            dbo2.sY(((bMt)bMx2.giP()).d());
                        }
                        dbo2.fa(fHs2.getId());
                        aAW.bUq().h((aAM)dbo2);
                    } else {
                        fSe.gFu().f("describedState", (Object)bMQ2);
                        fyD.popup((fRX)fRX2, (fEs)fEs2);
                        fEs2.a(fzQ.tJY, (fIs)new cHa(fEs2), true);
                    }
                } else if (string2.equals("glyph")) {
                    var11_11 = Integer.parseInt(string);
                    short s = GC.mS((int)var11_11);
                    short s3 = GC.mT((int)var11_11);
                    eSS eSS2 = eTo.fIZ().iY((long)s);
                    bMf bMf2 = new bMf(eSS2, s3);
                    if (fIq2.gBy() == fzQ.tJU) {
                        bMx bMx3;
                        fHs fHs4;
                        dbk dbk2 = new dbk(bMf2);
                        fHs fHs5 = fHs4 = fEs2.getElementMap().getId() == null ? fEs2.getElementMap().gAv() : fEs2.getElementMap();
                        if (fHs4 != null && (bMx3 = (bMx)fSe.gFu().aW("editableDescribedSpell", fHs4.getId())) != null) {
                            dbk2.sY(((bMt)bMx3.giP()).d());
                        }
                        dbk2.fa(fHs4.getId());
                        aAW.bUq().h((aAM)dbk2);
                    } else {
                        fSe.gFu().f("describedState", (Object)bMf2);
                        fyD.popup((fRX)fRX2, (fEs)fEs2);
                        fEs2.a(fzQ.tJY, (fIs)new cHb(fEs2), true);
                    }
                } else if (string2.equals("spell")) {
                    var11_11 = Integer.parseInt(string);
                    bMt bMt2 = bMB.eeV().If(var11_11);
                    if (bMt2 == null) {
                        return;
                    }
                    bMx bMx4 = new bMx(bMt2, 0, -1L, (exP)new bgO());
                    if (fIq2.gBy() == fzQ.tJU) {
                        fHs fHs6 = fEs2.getElementMap().getId() == null ? fEs2.getElementMap().gAv() : fEs2.getElementMap();
                        cDU.openSpellDescription((int)3, (bMx)bMx4, (String)fHs6.getId());
                    } else if (fRX3 != null) {
                        fSe.gFu().f("describedSpell", (Object)bMx4);
                        fyD.popup((fRX)fRX3, (fEs)fEs2);
                        fEs2.a(fzQ.tJY, (fIs)new cHc(fEs2), true);
                    }
                }
            }
        }
        if (fGB2 != null && fGB2.gyV() == fGC.uui) {
            fGK2 = fGB2.gyW();
            if (fGK2 == null) {
                return;
            }
            if (fGK2.gzE() == aHR.dSD) {
                fSe.gFu().f("describedState", null);
                string3 = ((fGL)fGK2).gzI();
                if (string3 == null) {
                    return;
                }
                stringArray = string3.split("_");
                string2 = stringArray[0];
                if (stringArray.length > 1) {
                    Object[] objectArray = stringArray[1].split(",");
                    string = aUM.cWf().c(string2, objectArray);
                } else {
                    string = aUM.cWf().c(string2, new Object[0]);
                }
                fSe.gFu().f("describedIcon", (Object)string);
                fyD.popup((fRX)fRX2, (fEs)fDy2);
                fEs2.a(fzQ.tJY, (fIs)new cHd(fEs2), true);
            }
        }
    }

    public static void updateBlocks(fIq fIq2, fEs fEs2, fRX fRX2, fRX fRX3) {
        fDy fDy2 = (fDy)fIq2.gBE();
        fGB fGB2 = fDy2.getBlockUnderMouse();
        if (fGB2 != null && mZg != fGB2.hashCode()) {
            mZg = fGB2.hashCode();
            cGZ.processText(fIq2, fEs2, fRX2, fRX3);
        }
    }

    public static void addSpellLevel(fIq fIq2) {
        fHs fHs2 = fIq2.gBD().getElementMap();
        if (fHs2 == null) {
            return;
        }
        bMx bMx2 = (bMx)fSe.gFu().aW("editableDescribedSpell", fHs2.getId());
        short s = GC.cu((long)(bMx2.cmL() + 1));
        if (s > MH.aWP.aVe()) {
            s = MH.aWP.aVe();
        }
        cGZ.b(s, fHs2);
    }

    public static void removeSpellLevel(fIq fIq2) {
        fHs fHs2 = fIq2.gBD().getElementMap();
        if (fHs2 == null) {
            return;
        }
        bMx bMx2 = (bMx)fSe.gFu().aW("editableDescribedSpell", fHs2.getId());
        short s = GC.cu((long)(bMx2.cmL() - 1));
        if (s < 0) {
            s = 0;
        }
        cGZ.b(s, fHs2);
    }

    public static void restore(fIq fIq2) {
        fHs fHs2 = fIq2.gBD().getElementMap();
        if (fHs2 == null) {
            return;
        }
        short s = (Short)fSe.gFu().aW("describedSpellRealLevel", fHs2.getId());
        cGZ.b(s, fHs2);
    }

    private static void b(short s, fHs fHs2) {
        bMx bMx2 = (bMx)fSe.gFu().aW("editableDescribedSpell", fHs2.getId());
        if (bMx2 == null) {
            return;
        }
        bMx2.cj(s);
        fDh fDh2 = (fDh)fHs2.uH("tabbedContainer");
        if (fDh2 == null) {
            return;
        }
        boolean bl = fDh2.getSelectedTabIndex() == 0;
        fSe.gFu().a((aEF)bMx2, new String[]{"level", "levelTextShort", "ap", "castInterval", "wp", "chrage", "mp", "castOnlyInLine", "range", "areaOfEffectIconURL", "conditionsDescription", "criticalDescription", "shortDescription", "testLineOfSight", "modifiableRange", "hasEvolutionCondition", "evolutionText", "shortOrCriticalDescription"});
        cGZ.a((Qk)bMx2, bMx2, bl);
    }

    public static void updateSpellLevel(fLV fLV2) {
        fHs fHs2 = fLV2.gBE().getElementMap();
        bMx bMx2 = (bMx)fSe.gFu().aW("editableDescribedSpell", fHs2.getId());
        bMx2.id(fLV2.bqr());
    }

    private static void a(Qk qk, bMx bMx2, boolean bl) {
        for (eNk eNk2 : qk) {
            boolean bl2 = eNk2.df(1L);
            if (bl2 && bl || !bl2 && !bl || bMx2.cmL() > eNk2.fAw() || bMx2.cmL() < eNk2.fAv()) continue;
            int n = eNk2.fAn();
            Object[] objectArray = new Object[n];
            for (int i = 0; i < n; ++i) {
                objectArray[i] = eNk2.a(i, bMx2.cmL(), eNe.qPu);
            }
            if (eNh.qWn.contains(eNk2.avZ())) {
                cGZ.a((Qk)bMi.giD().Za(eNk2.aZH()), bMx2, bl);
                continue;
            }
            if (eNk2.avZ() == eNf.qUR.d()) {
                cYq.eXS().ac(((bMt)bMx2.giP()).d(), eNk2.a(0, bMx2.cmL(), eNe.qPu), (short)eNk2.a(1, bMx2.cmL(), eNe.qPu));
                continue;
            }
            QQ qQ = eMt.c((int)eNk2.avZ(), (Object[])objectArray);
            if (qQ == null) continue;
            cGZ.a((Qk)qQ, bMx2, bl);
        }
    }

    public static void openCloseDescription(fLG fLG2, String string) {
        bMx bMx2;
        if (fLG2 == null || fLG2.getItemValue() == null) {
            return;
        }
        if (fLG2.getItemValue() instanceof bMx) {
            bMx2 = (bMx)fLG2.getItemValue();
        } else if (fLG2.getItemValue() instanceof bMD) {
            bMx2 = ((bMD)fLG2.getItemValue()).eeW();
        } else if (fLG2.getItemValue() instanceof bMt) {
            bgT bgT2 = cVu.eUm() != null ? cVu.eUm() : aUE.cVJ().cVK();
            bMx2 = new bMx((bMt)fLG2.getItemValue(), bgT2.cmL(), -1L, (exP)bgT2);
        } else {
            return;
        }
        if (bMx2 == null) {
            return;
        }
        cGZ.openCloseDescription(fLG2, bMx2, string);
    }

    public static void openCloseDescription(fLG fLG2, bMx bMx2, String string) {
        if (fLG2 == null || fLG2.getItemValue() == null) {
            return;
        }
        if (bMx2 == null) {
            return;
        }
        exP exP2 = bMx2.eeL();
        bMx bMx3 = bMx2.ic(false);
        if (exP2 != null) {
            bMx3.cj(bMx2.c(exP2.dnM()));
        }
        fSe.gFu().f("describedSpell", (Object)bMx3);
        fSe.gFu().f("describedSpellRealLevel", (Object)bMx3.cmL());
        fAW fAW2 = (fAW)fLG2.gBE();
        fRX fRX2 = (fRX)fAW2.getElementMap().uH(string);
        if (fLG2.gBy() == fzQ.tJE && !fBJ.getInstance().isDragging()) {
            fyD.popup((fRX)fRX2, (fEs)fAW2);
        } else if (fLG2.gBy() == fzQ.tJD || fLG2.gBy() == fzQ.tJC) {
            fSe.gFu().f("describedSpell", null);
            fSe.gFu().f("describedSpellRealLevel", (Object)-1);
            fyD.closePopup((fIq)fLG2, (fRX)fRX2);
        }
    }
}
