/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  Bw
 *  GC
 *  Ns
 *  aAM
 *  aBg
 *  aEF
 *  aUE
 *  arx
 *  ayF
 *  bMx
 *  bdj
 *  bgT
 *  bjc
 *  bmF
 *  cDk
 *  cDl
 *  com.ankamagames.wakfu.client.console.command.debug.anim.AnmDebuggerCommand
 *  fAD
 *  fAS
 *  fAx
 *  fDu
 *  fIq
 *  fLP
 *  fLW
 *  fSe
 *  fyw
 *  fzQ
 *  org.apache.log4j.Logger
 */
import com.ankamagames.wakfu.client.console.command.debug.anim.AnmDebuggerCommand;
import java.util.ArrayList;
import org.apache.log4j.Logger;

@fyF
public class cDj {
    protected static final Logger mSX = Logger.getLogger(cDj.class);
    public static final String PACKAGE = "wakfu.adminCharacterEditor";
    private static final ArrayList<cDl> mSY = new ArrayList();
    private static final ArrayList<cDl> mSZ = new ArrayList();

    public static void openCharacterColorEditor(fIq fIq2) {
        if (fyw.gqw().to("adminCharacterEditorDialog")) {
            bgT bgT2 = aUE.cVJ().cVK();
            mSY.clear();
            mSZ.clear();
            for (arx arx2 : arx.values()) {
                bjc bjc2 = new bjc(GC.aNJ(), GC.aNJ(), GC.aNJ());
                if (arx2.bHJ() >= arx.cTB.bHJ()) {
                    mSY.add(new cDl(bjc2, arx2));
                    continue;
                }
                mSZ.add(new cDl(bjc2, arx2));
            }
            cDj.reloadAnmimation(null);
            fSe.gFu().f("adminColors", mSY);
            fSe.gFu().f("adminInactiveColors", mSZ);
            cCJ.pd("adminCharacterColorEditorDialog");
            fyw.gqw().tl("adminCharacterEditorDialog");
        } else {
            cCJ.pd("adminCharacterEditorDialog");
            fyw.gqw().tl("adminCharacterColorEditorDialog");
            fSe.gFu().vX("adminAnimDirection");
            fSe.gFu().vX("adminAnimName");
            fSe.gFu().vX("adminColors");
            fSe.gFu().vX("adminInactiveColors");
        }
    }

    public static void loadAnmDebugger(fIq fIq2) {
        if (fyw.gqw().to("debugAnmDialog")) {
            fyw.gqw().tl("debugAnmDialog");
        } else {
            AnmDebuggerCommand.cUf();
        }
    }

    public static void reloadAnmimation(fIq fIq2) {
        bgT bgT2 = aUE.cVJ().cVK();
        bdj bdj2 = bgT2.ddI();
        fSe.gFu().a((aEF)bgT2, new String[]{"actorDescriptorLibrary"});
        fSe.gFu().a((aEF)bgT2, new String[]{"actorEquipment"});
        fSe.gFu().f("adminAnimDirection", (Object)bdj2.bcB().dzy);
        fSe.gFu().f("adminAnimName", (Object)bdj2.bpT());
    }

    public static void deleteActiveColor(fIq fIq2, cDl cDl2) {
        mSY.remove(cDl2);
        mSZ.add(cDl2);
        fSe.gFu().f("adminColors", null);
        fSe.gFu().f("adminInactiveColors", null);
        fSe.gFu().f("adminColors", mSY);
        fSe.gFu().f("adminInactiveColors", mSZ);
    }

    public static void activateColor(fIq fIq2) {
        fAS fAS2 = (fAS)fIq2.gBE().getElementMap().uH("comboColor");
        cDl cDl2 = (cDl)fAS2.getSelectedValue();
        mSZ.remove(cDl2);
        mSY.add(cDl2);
        fSe.gFu().f("adminColors", null);
        fSe.gFu().f("adminInactiveColors", null);
        fSe.gFu().f("adminColors", mSY);
        fSe.gFu().f("adminInactiveColors", mSZ);
    }

    public static void setFilterRed(fLW fLW2, cDl cDl2) {
        if (cDl2 != null) {
            cDl2.i(fLW2.getValue());
            cDl2.a((fAx)fLW2.gBD().getElementMap().uH("localPlayerDisplay"));
        }
    }

    public static void setFilterGreen(fLW fLW2, cDl cDl2) {
        if (cDl2 != null) {
            cDl2.j(fLW2.getValue());
            cDl2.a((fAx)fLW2.gBD().getElementMap().uH("localPlayerDisplay"));
        }
    }

    public static void setFilterBlue(fLW fLW2, cDl cDl2) {
        if (cDl2 != null) {
            cDl2.k(fLW2.getValue());
            cDl2.a((fAx)fLW2.gBD().getElementMap().uH("localPlayerDisplay"));
        }
    }

    public static void setFilterRed(fIq fIq2, fDu fDu2, cDl cDl2) {
        if (fDu2.getText().length() == 0) {
            return;
        }
        float f = (float)Bw.r((Object)fDu2.getText()) / 255.0f;
        cDl2.i(f);
        cDl2.a((fAx)fIq2.gBD().getElementMap().uH("localPlayerDisplay"));
    }

    public static void setFilterGreen(fIq fIq2, fDu fDu2, cDl cDl2) {
        if (fDu2.getText().length() == 0) {
            return;
        }
        float f = (float)Bw.r((Object)fDu2.getText()) / 255.0f;
        cDl2.j(f);
        cDl2.a((fAx)fIq2.gBD().getElementMap().uH("localPlayerDisplay"));
    }

    public static void setFilterBlue(fIq fIq2, fDu fDu2, cDl cDl2) {
        if (fIq2.gBy() != fzQ.tJH) {
            return;
        }
        if (fDu2.getText().length() == 0) {
            return;
        }
        float f = (float)Bw.r((Object)fDu2.getText()) / 255.0f;
        cDl2.k(f);
        cDl2.a((fAx)fIq2.gBD().getElementMap().uH("localPlayerDisplay"));
    }

    public static void applyColor(fIq fIq2, cDl cDl2) {
        cDl2.a((fAx)fIq2.gBD().getElementMap().uH("localPlayerDisplay"));
    }

    private static void a(fIq fIq2) {
        fAD fAD2 = (fAD)fIq2.gBD().getElementMap().uH("applyColorButton");
        fAD2.setEnabled(true);
    }

    public static void validLevel(fLP fLP2) {
        fDu fDu2 = (fDu)fyw.gqw().gqC().uR("adminCharacterEditorDialog").uH("level");
        if (fDu2 == null || fDu2.getText() == null || fDu2.getText().length() == 0) {
            return;
        }
        ayF ayF2 = aUE.cVJ().etu();
        if (ayF2 == null) {
            aQh.cBI().jI("Pour acc\u00e9der \u00e0 ces commandes il faut \u00eatre connect\u00e9 !");
            return;
        }
        Ns ns = new Ns();
        ns.C((byte)3);
        ns.Q((short)21);
        ns.R(Short.parseShort(fDu2.getText()));
        ayF2.d((aAM)ns);
        cDj.eec();
    }

    public static void validSpellLevel(fLP fLP2, bMx bMx2, fDu fDu2) {
        ayF ayF2 = aUE.cVJ().etu();
        if (ayF2 == null) {
            aQh.cBI().jI("Pour acc\u00e9der \u00e0 ces commandes il faut \u00eatre connect\u00e9 !");
            return;
        }
        Ns ns = new Ns();
        ns.C((byte)3);
        ns.Q((short)324);
        ns.nX(bMx2.avr());
        ns.R(Short.parseShort(fDu2.getText()));
        ayF2.d((aAM)ns);
        cDj.eec();
    }

    public static void learnSkill(fLP fLP2, bmF bmF2) {
        ayF ayF2 = aUE.cVJ().etu();
        if (ayF2 == null) {
            aQh.cBI().jI("Pour acc\u00e9der \u00e0 ces commandes il faut \u00eatre connect\u00e9 !");
            return;
        }
        Ns ns = new Ns();
        ns.C((byte)3);
        ns.Q((short)229);
        ns.nX(bmF2.dwk());
        ayF2.d((aAM)ns);
        cDj.eec();
    }

    public static void addSkillXp(fLP fLP2, bmF bmF2, fDu fDu2) {
        ayF ayF2 = aUE.cVJ().etu();
        if (ayF2 == null) {
            aQh.cBI().jI("Pour acc\u00e9der \u00e0 ces commandes il faut \u00eatre connect\u00e9 !");
            return;
        }
        long l = 0L;
        try {
            l = Long.parseLong(fDu2.getText());
        }
        catch (Exception exception) {
            mSX.error((Object)"Exception during addSkillXp", (Throwable)exception);
        }
        fDu2.setText("0");
        Ns ns = new Ns();
        ns.C((byte)3);
        ns.Q((short)34);
        ns.nX(bmF2.dwk());
        ns.cX(l);
        ayF2.d((aAM)ns);
        cDj.eec();
    }

    private static void eec() {
        aBg.bUP().a((Runnable)new cDk(), 1500L, 1);
    }
}
