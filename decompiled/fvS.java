/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvS
implements aqz {
    protected int efP;
    protected fvT[] tzx;

    public int cjd() {
        return this.efP;
    }

    public fvT[] gor() {
        return this.tzx;
    }

    @Override
    public void reset() {
        this.efP = 0;
        this.tzx = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.efP = aqH2.bGI();
        int n = aqH2.bGI();
        this.tzx = new fvT[n];
        for (int i = 0; i < n; ++i) {
            this.tzx[i] = new fvT();
            this.tzx[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBh.d();
    }
}
