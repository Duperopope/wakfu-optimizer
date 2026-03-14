/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuu
implements aqz {
    protected int o;
    protected short euL;
    protected fuv[] tyy;

    public int d() {
        return this.o;
    }

    public short cyv() {
        return this.euL;
    }

    public fuv[] gnr() {
        return this.tyy;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.euL = 0;
        this.tyy = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.euL = aqH2.bGG();
        int n = aqH2.bGI();
        this.tyy = new fuv[n];
        for (int i = 0; i < n; ++i) {
            this.tyy[i] = new fuv();
            ((fuV)this.tyy[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAY.d();
    }
}
