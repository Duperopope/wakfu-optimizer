/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvM
implements aqz {
    protected int o;
    protected fvP[] tzu;
    protected fvd tyG;

    public int d() {
        return this.o;
    }

    public fvP[] goo() {
        return this.tzu;
    }

    public fvd gnz() {
        return this.tyG;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tzu = null;
        this.tyG = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        int n = aqH2.bGI();
        this.tzu = new fvP[n];
        for (int i = 0; i < n; ++i) {
            this.tzu[i] = new fvP();
            this.tzu[i].a(aqH2);
        }
        if (aqH2.aTf() != 0) {
            this.tyG = new fvd();
            this.tyG.a(aqH2);
        } else {
            this.tyG = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyV.d();
    }
}
