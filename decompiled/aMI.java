/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aMI
implements aqz {
    protected int o;
    protected int eln;
    protected aMJ[] elo;

    public int d() {
        return this.o;
    }

    public int coF() {
        return this.eln;
    }

    public aMJ[] coG() {
        return this.elo;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eln = 0;
        this.elo = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eln = aqH2.bGI();
        int n = aqH2.bGI();
        this.elo = new aMJ[n];
        for (int i = 0; i < n; ++i) {
            this.elo[i] = new aMJ();
            this.elo[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAs.d();
    }
}
