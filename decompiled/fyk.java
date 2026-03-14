/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fyk
implements aqz {
    protected int elt;
    protected fyl[] tBx;

    public int coK() {
        return this.elt;
    }

    public fyl[] gqq() {
        return this.tBx;
    }

    @Override
    public void reset() {
        this.elt = 0;
        this.tBx = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.elt = aqH2.bGI();
        int n = aqH2.bGI();
        this.tBx = new fyl[n];
        for (int i = 0; i < n; ++i) {
            this.tBx[i] = new fyl();
            this.tBx[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozJ.d();
    }
}
