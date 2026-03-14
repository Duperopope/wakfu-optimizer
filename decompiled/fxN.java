/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fxN
implements aqz {
    protected int o;
    protected int ehb;
    protected fvd tyG;

    public int d() {
        return this.o;
    }

    public int ckr() {
        return this.ehb;
    }

    public fvd gnz() {
        return this.tyG;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehb = 0;
        this.tyG = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehb = aqH2.bGI();
        if (aqH2.aTf() != 0) {
            this.tyG = new fvd();
            this.tyG.a(aqH2);
        } else {
            this.tyG = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozW.d();
    }
}
