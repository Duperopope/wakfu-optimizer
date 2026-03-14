/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fwZ
implements aqz {
    protected int o;
    protected int epa;
    protected int epb;

    public int d() {
        return this.o;
    }

    public int csE() {
        return this.epa;
    }

    public int csF() {
        return this.epb;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.epa = 0;
        this.epb = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.epa = aqH2.bGI();
        this.epb = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.ozn.d();
    }
}
