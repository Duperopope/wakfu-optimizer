/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aKU
implements aqz {
    protected int o;
    protected int egx;
    protected String bds;

    public int d() {
        return this.o;
    }

    public int cjJ() {
        return this.egx;
    }

    public String aXE() {
        return this.bds;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.egx = 0;
        this.bds = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.egx = aqH2.bGI();
        this.bds = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.oyt.d();
    }
}
