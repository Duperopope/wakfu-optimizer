/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fwe
implements aqz {
    protected int o;
    protected int elr;
    protected int els;
    protected short tzC;
    protected short tzD;
    protected short tzE;
    protected short tzF;
    protected int elt;
    protected fwf[] tzG;
    protected fwf[] tzH;
    protected fwh[] tzI;

    public int d() {
        return this.o;
    }

    public int blh() {
        return this.elr;
    }

    public int rI() {
        return this.els;
    }

    public short gow() {
        return this.tzC;
    }

    public short gox() {
        return this.tzD;
    }

    public short goy() {
        return this.tzE;
    }

    public short goz() {
        return this.tzF;
    }

    public int coK() {
        return this.elt;
    }

    public fwf[] goA() {
        return this.tzG;
    }

    public fwf[] goB() {
        return this.tzH;
    }

    public fwh[] goC() {
        return this.tzI;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.elr = 0;
        this.els = 0;
        this.tzC = 0;
        this.tzD = 0;
        this.tzE = 0;
        this.tzF = 0;
        this.elt = 0;
        this.tzG = null;
        this.tzH = null;
        this.tzI = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.elr = aqH2.bGI();
        this.els = aqH2.bGI();
        this.tzC = aqH2.bGG();
        this.tzD = aqH2.bGG();
        this.tzE = aqH2.bGG();
        this.tzF = aqH2.bGG();
        this.elt = aqH2.bGI();
        int n3 = aqH2.bGI();
        this.tzG = new fwf[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tzG[n2] = new fwf();
            ((fwF)this.tzG[n2]).a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tzH = new fwf[n2];
        for (n = 0; n < n2; ++n) {
            this.tzH[n] = new fwf();
            ((fwF)this.tzH[n]).a(aqH2);
        }
        n = aqH2.bGI();
        this.tzI = new fwh[n];
        for (int i = 0; i < n; ++i) {
            this.tzI[i] = new fwh();
            ((fwH)this.tzI[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBe.d();
    }
}
