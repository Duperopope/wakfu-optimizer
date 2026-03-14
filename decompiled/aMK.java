/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aMK
implements aqz {
    protected int o;
    protected int elq;
    protected int ejx;
    protected int efP;
    protected int cip;

    public int d() {
        return this.o;
    }

    public int coJ() {
        return this.elq;
    }

    public int cmP() {
        return this.ejx;
    }

    public int cjd() {
        return this.efP;
    }

    public int getSoundId() {
        return this.cip;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.elq = 0;
        this.ejx = 0;
        this.efP = 0;
        this.cip = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.elq = aqH2.bGI();
        this.ejx = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.cip = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oAm.d();
    }
}
