/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fxt
implements aqz {
    protected int epK;
    protected fxu[] tAV;
    protected fxv[] tAW;

    public int ctn() {
        return this.epK;
    }

    public fxu[] gpO() {
        return this.tAV;
    }

    public fxv[] gpP() {
        return this.tAW;
    }

    @Override
    public void reset() {
        this.epK = 0;
        this.tAV = null;
        this.tAW = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        this.epK = aqH2.bGI();
        int n2 = aqH2.bGI();
        this.tAV = new fxu[n2];
        for (n = 0; n < n2; ++n) {
            this.tAV[n] = new fxu();
            this.tAV[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.tAW = new fxv[n];
        for (int i = 0; i < n; ++i) {
            this.tAW[i] = new fxv();
            ((fxV)this.tAW[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozv.d();
    }
}
