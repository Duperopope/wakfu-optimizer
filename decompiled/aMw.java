/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aMw
implements aqz {
    protected int efP;
    protected short ekF;
    protected int ekG;
    protected int egx;
    protected aMx[] ekH;

    public int cjd() {
        return this.efP;
    }

    public short cnT() {
        return this.ekF;
    }

    public int bnd() {
        return this.ekG;
    }

    public int cjJ() {
        return this.egx;
    }

    public aMx[] cnU() {
        return this.ekH;
    }

    @Override
    public void reset() {
        this.efP = 0;
        this.ekF = 0;
        this.ekG = 0;
        this.egx = 0;
        this.ekH = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.efP = aqH2.bGI();
        this.ekF = aqH2.bGG();
        this.ekG = aqH2.bGI();
        this.egx = aqH2.bGI();
        int n = aqH2.bGI();
        this.ekH = new aMx[n];
        for (int i = 0; i < n; ++i) {
            this.ekH[i] = new aMx();
            this.ekH[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBh.d();
    }
}
