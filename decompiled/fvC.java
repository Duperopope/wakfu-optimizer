/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvC
implements aqz {
    protected int o;
    protected short aXy;
    protected String[] ejR;
    protected int bMn;
    protected int efU;
    protected String eik;
    protected int[] ejS;
    protected int[] ejT;

    public int d() {
        return this.o;
    }

    public short clb() {
        return this.aXy;
    }

    public String[] cng() {
        return this.ejR;
    }

    public int getDuration() {
        return this.bMn;
    }

    public int cji() {
        return this.efU;
    }

    public String clB() {
        return this.eik;
    }

    public int[] cnh() {
        return this.ejS;
    }

    public int[] cni() {
        return this.ejT;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.aXy = 0;
        this.ejR = null;
        this.bMn = 0;
        this.efU = 0;
        this.eik = null;
        this.ejS = null;
        this.ejT = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.aXy = aqH2.bGG();
        this.ejR = aqH2.bGO();
        this.bMn = aqH2.bGI();
        this.efU = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        this.ejS = aqH2.bGM();
        this.ejT = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.ozS.d();
    }
}
