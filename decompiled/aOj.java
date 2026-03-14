/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOj
implements aqz {
    protected int o;
    protected aOk[] eqC;

    public int d() {
        return this.o;
    }

    public aOk[] cue() {
        return this.eqC;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eqC = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        int n = aqH2.bGI();
        this.eqC = new aOk[n];
        for (int i = 0; i < n; ++i) {
            this.eqC[i] = new aOk();
            ((aOK)this.eqC[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBm.d();
    }
}
