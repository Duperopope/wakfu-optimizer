/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuD
implements aqz {
    protected int o;
    protected int bIi;
    protected String[] atp;

    public int d() {
        return this.o;
    }

    public int aeV() {
        return this.bIi;
    }

    public String[] aHm() {
        return this.atp;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.bIi = 0;
        this.atp = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.bIi = aqH2.bGI();
        this.atp = aqH2.bGO();
    }

    @Override
    public final int bGA() {
        return ewj.oAb.d();
    }
}
