/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aKX
implements aqz {
    protected int o;
    protected String p;
    protected boolean egz;

    public int d() {
        return this.o;
    }

    public String getName() {
        return this.p;
    }

    public boolean cjL() {
        return this.egz;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.p = null;
        this.egz = false;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.p = aqH2.bGL().intern();
        this.egz = aqH2.bxv();
    }

    @Override
    public final int bGA() {
        return ewj.oys.d();
    }
}
