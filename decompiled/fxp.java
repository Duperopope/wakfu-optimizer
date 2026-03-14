/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fxp
implements aqz {
    protected int epK;
    protected int ely;
    protected int epL;
    protected int epM;
    protected int epN;
    protected int epO;
    protected int epP;
    protected int epQ;
    protected int epR;
    protected int epS;
    protected int epT;
    protected int epU;
    protected short egr;
    protected int[] epV;
    protected fxs[] tAS;
    protected fxq[] tAT;
    protected fxr[] tAU;

    public int ctn() {
        return this.epK;
    }

    public int coQ() {
        return this.ely;
    }

    public int cto() {
        return this.epL;
    }

    public int ctp() {
        return this.epM;
    }

    public int ctq() {
        return this.epN;
    }

    public int ctr() {
        return this.epO;
    }

    public int cts() {
        return this.epP;
    }

    public int Xt() {
        return this.epQ;
    }

    public int ctt() {
        return this.epR;
    }

    public int ctu() {
        return this.epS;
    }

    public int ctv() {
        return this.epT;
    }

    public int ctw() {
        return this.epU;
    }

    public short cjD() {
        return this.egr;
    }

    public int[] ctx() {
        return this.epV;
    }

    public fxs[] gpL() {
        return this.tAS;
    }

    public fxq[] gpM() {
        return this.tAT;
    }

    public fxr[] gpN() {
        return this.tAU;
    }

    @Override
    public void reset() {
        this.epK = 0;
        this.ely = 0;
        this.epL = 0;
        this.epM = 0;
        this.epN = 0;
        this.epO = 0;
        this.epP = 0;
        this.epQ = 0;
        this.epR = 0;
        this.epS = 0;
        this.epT = 0;
        this.epU = 0;
        this.egr = 0;
        this.epV = null;
        this.tAS = null;
        this.tAT = null;
        this.tAU = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        this.epK = aqH2.bGI();
        this.ely = aqH2.bGI();
        this.epL = aqH2.bGI();
        this.epM = aqH2.bGI();
        this.epN = aqH2.bGI();
        this.epO = aqH2.bGI();
        this.epP = aqH2.bGI();
        this.epQ = aqH2.bGI();
        this.epR = aqH2.bGI();
        this.epS = aqH2.bGI();
        this.epT = aqH2.bGI();
        this.epU = aqH2.bGI();
        this.egr = aqH2.bGG();
        this.epV = aqH2.bGM();
        int n3 = aqH2.bGI();
        this.tAS = new fxs[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tAS[n2] = new fxs();
            ((fxS)this.tAS[n2]).a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tAT = new fxq[n2];
        for (n = 0; n < n2; ++n) {
            this.tAT[n] = new fxq();
            ((fxQ)this.tAT[n]).a(aqH2);
        }
        n = aqH2.bGI();
        this.tAU = new fxr[n];
        for (int i = 0; i < n; ++i) {
            this.tAU[i] = new fxr();
            this.tAU[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozs.d();
    }
}
