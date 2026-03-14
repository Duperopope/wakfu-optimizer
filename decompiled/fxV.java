/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fxV
implements aqz {
    protected int o;
    protected int[] erx;
    protected String ery;

    public int d() {
        return this.o;
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
        this.erx = null;
        this.ery = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.erx = aqH2.bGM();
        this.ery = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.ozC.d();
    }
}
