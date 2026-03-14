/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvo
implements aqz {
    protected int o;
    protected int cDu;
    protected int ehb;
    protected int ehc;
    protected int[] eji;
    protected fvd tyG;

    public int d() {
        return this.o;
    }

    public int bBE() {
        return this.cDu;
    }

    public int ckr() {
        return this.ehb;
    }

    public int cks() {
        return this.ehc;
    }

    public int[] cmy() {
        return this.eji;
    }

    public fvd gnz() {
        return this.tyG;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.cDu = 0;
        this.ehb = 0;
        this.ehc = 0;
        this.eji = null;
        this.tyG = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.cDu = aqH2.bGI();
        this.ehb = aqH2.bGI();
        this.ehc = aqH2.bGI();
        this.eji = aqH2.bGM();
        if (aqH2.aTf() != 0) {
            this.tyG = new fvd();
            this.tyG.a(aqH2);
        } else {
            this.tyG = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyO.d();
    }
}
