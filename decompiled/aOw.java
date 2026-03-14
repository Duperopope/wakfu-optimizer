/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOw
implements aqz {
    protected int o;
    protected int erv;
    protected String erw;
    protected int[] erx;
    protected String ery;

    public int d() {
        return this.o;
    }

    public int cuX() {
        return this.erv;
    }

    public String cuY() {
        return this.erw;
    }

    public int[] cuZ() {
        return this.erx;
    }

    public String cva() {
        return this.ery;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.erv = 0;
        this.erw = null;
        this.erx = null;
        this.ery = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.erv = aqH2.bGI();
        this.erw = aqH2.bGL().intern();
        this.erx = aqH2.bGM();
        this.ery = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.ozC.d();
    }
}
