/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  PV
 *  QQ
 *  Qu
 *  aCd
 *  eNl
 *  eTU
 *  eTm
 *  eUK
 *  eUb
 *  eUg
 *  eWc
 *  eXe
 *  eXx
 *  ewo
 *  ewr
 *  exP
 *  fqH
 *  fqS
 *  org.apache.log4j.Logger
 */
import java.util.List;
import org.apache.log4j.Logger;

final class eUL
extends eUg<fqE, exP> {
    private static final Logger rxY = Logger.getLogger(eUL.class);
    private final eWc rxZ = new eWc();
    private boolean rya = true;

    eUL(eTU eTU2) {
        super(eTU2);
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    fqH a(exP exP2, fqE fqE2, aCd aCd2, boolean bl) {
        fqH fqH2;
        if (fqE2 == null) {
            rxY.error((Object)this.rrZ.sq("casting a null SpellLevel"));
            return fqH.sUU;
        }
        Object Spell = fqE2.giP();
        if (Spell == null) {
            rxY.error((Object)this.rrZ.sq("casting a SpellLevel with a null spell"));
            return fqH.sUU;
        }
        if (eUK.b(Spell)) {
            return fqH.sVl;
        }
        if (exP2.a((PV)eXe.rEP)) {
            return fqH.sVq;
        }
        if (ewo.oBF.o(ewr.oDD).contains(((fqD)Spell).d())) {
            return fqH.sVq;
        }
        if (!eUK.a((exP)exP2, Spell)) {
            return fqH.sVk;
        }
        if (bl) {
            if (!eUK.c((exP)exP2, (fqE)fqE2, Spell)) {
                return fqH.sUY;
            }
            if (!eUK.b((exP)exP2, (fqE)fqE2, Spell)) {
                return fqH.sUZ;
            }
            if (!eUK.a((exP)exP2, (fqE)fqE2, Spell)) {
                return fqH.sVa;
            }
            if (!eUK.a((exP)exP2, (eXx)eXx.rGQ, (fqE)fqE2, Spell)) {
                return fqH.sVb;
            }
            if (!eUK.d((exP)exP2, (fqE)fqE2, Spell)) {
                return fqH.sVc;
            }
            if (!eUK.e((exP)exP2, (fqE)fqE2, Spell)) {
                return fqH.sVd;
            }
        }
        if (!(fqH2 = exP2.fgh().c(exP2, fqE2, (int)this.rrZ.dHf().bhJ())).isValid()) {
            return fqH2;
        }
        int n = ((fqD)Spell).j(fqE2, exP2, aCd2, this.rrZ.bbh());
        int n2 = ((fqD)Spell).i(fqE2, exP2, aCd2, this.rrZ.bbh());
        boolean bl2 = ((fqD)Spell).d(fqE2, (Object)exP2, (Object)aCd2, (Object)this.rrZ.bbh());
        int n3 = this.a((Qu)exP2, bl2, n, n2);
        this.rxZ.a((eUb)this.rrZ, exP2, fqE2, n, n3, aCd2);
        if (this.rya) {
            this.rxZ.fNE();
        }
        fqH fqH3 = fqH.sVr;
        try {
            if (aCd2 != null) {
                exP exP3 = this.rrZ.dy(aCd2.getX(), aCd2.getY());
                if (!this.a(exP2, aCd2, fqE2, exP3, this.rrZ, n, n3)) {
                    fqH fqH4 = fqH.sVj;
                    return fqH4;
                }
                List list = this.rrZ.a(aCd2);
                for (Qu qu : list) {
                    fqH fqH5 = exP2.fgh().a(exP2, fqE2, (int)this.rrZ.dHf().bhJ(), (anU)qu);
                    if (fqH5.isValid()) continue;
                    fqH fqH6 = fqH5;
                    return fqH6;
                }
            }
            fqH3 = this.a((Qu)exP2, fqE2, aCd2, bl2, n, n2, ((fqD)Spell).a(fqE2, (Object)exP2, (Object)aCd2, (Object)this.rrZ.bbh()), ((fqD)Spell).f(fqE2, exP2, (Object)aCd2, (Object)this.rrZ.bbh()), ((fqD)Spell).fYo(), ((fqD)Spell).l(fqE2, exP2, aCd2, this.rrZ.bbh()), ((fqD)Spell).giF());
        }
        catch (Exception exception) {
            rxY.error((Object)"Exception levee", (Throwable)exception);
        }
        finally {
            this.rxZ.clear();
        }
        return fqH3;
    }

    public boolean a(exP exP2, fqE fqE2, int n, int n2, boolean bl, int n3, int n4) {
        if (((fqD)fqE2.giP()).g(fqS.sWo) && this.b(exP2, n3, n4)) {
            return true;
        }
        if (((fqD)fqE2.giP()).g(fqS.sWq) && this.c(exP2, n3, n4)) {
            return true;
        }
        if (!((fqD)fqE2.giP()).g(fqS.sWm)) {
            return super.a((Qu)exP2, (eNl)fqE2, n, n2, bl, n3, n4);
        }
        if (!this.rxZ.fNF()) {
            return super.a((Qu)exP2, (eNl)fqE2, n, n2, bl, n3, n4);
        }
        boolean bl2 = this.rxZ.fNG();
        if (!bl2) {
            return super.a((Qu)exP2, (eNl)fqE2, n, n2, bl, n3, n4);
        }
        return bl2;
    }

    private boolean b(exP exP2, int n, int n2) {
        List list = this.rrZ.bai().g(new aCd(n, n2));
        boolean bl = false;
        for (QQ qQ : list) {
            if (qQ.aeV() != eTm.rnG.aHp() || qQ.bcP() != exP2.bcP()) continue;
            bl = true;
        }
        return bl;
    }

    private boolean c(exP exP2, int n, int n2) {
        List list = this.rrZ.bai().g(new aCd(n, n2));
        boolean bl = false;
        for (QQ qQ : list) {
            Qu qu;
            if (qQ.aeV() != eTm.rnr.aHp() || (qu = qQ.bci()) == null || qu.Sn() != exP2.Sn()) continue;
            bl = true;
        }
        return bl;
    }

    protected boolean a(exP exP2, fqE fqE2, int n, int n2, short s, int n3, int n4, boolean bl) {
        if (((fqD)fqE2.giP()).g(fqS.sWo) && this.b(exP2, n, n2)) {
            return true;
        }
        if (((fqD)fqE2.giP()).g(fqS.sWq) && this.c(exP2, n, n2)) {
            return true;
        }
        if (!((fqD)fqE2.giP()).g(fqS.sWm)) {
            return super.a((Qu)exP2, (eNl)fqE2, n, n2, s, n3, n4, bl);
        }
        if (!this.rxZ.fNF()) {
            return super.a((Qu)exP2, (eNl)fqE2, n, n2, s, n3, n4, bl);
        }
        boolean bl2 = this.rxZ.fNI();
        if (!bl2) {
            return super.a((Qu)exP2, (eNl)fqE2, n3, n4, bl, n, n2) && eUL.a((exP)exP2, (aCd)new aCd(n, n2), (fqE)fqE2, null, (eTU)this.rrZ) && super.a((Qu)exP2, (eNl)fqE2, n, n2, s, n3, n4, bl);
        }
        return bl2;
    }

    boolean a(exP exP2, aCd aCd2, fqE fqE2, exP exP3, eTU eTU2, int n, int n2) {
        Object Spell = fqE2.giP();
        boolean bl = ((fqD)Spell).b(fqE2, (Object)exP2, (Object)aCd2, (Object)eTU2.bbh());
        boolean bl2 = ((fqD)Spell).k(fqE2, exP2, aCd2, eTU2.bbh());
        if (!bl && !bl2) {
            return true;
        }
        boolean bl3 = ((fqD)Spell).c(fqE2, (Object)exP2, (Object)aCd2, (Object)eTU2.bbh());
        boolean bl4 = eUL.a((exP)exP2, (aCd)aCd2, (fqE)fqE2, (exP)exP3, (eTU)eTU2, (boolean)bl3);
        if (!((fqD)Spell).g(fqS.sWm)) {
            return bl4;
        }
        if (!this.rxZ.fNF()) {
            return bl4;
        }
        boolean bl5 = this.rxZ.fNH();
        if (!bl5) {
            boolean bl6 = ((fqD)Spell).l(fqE2, exP2, aCd2, eTU2.bbh());
            boolean bl7 = super.a((Qu)exP2, (eNl)fqE2, n, n2, bl6, aCd2.getX(), aCd2.getY());
            return bl7 && bl4;
        }
        return bl5;
    }

    public void fMA() {
        this.rya = false;
    }

    public void fMB() {
        this.rya = true;
    }
}
