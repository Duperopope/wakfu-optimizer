/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fyj
implements aqz {
    protected int o;
    protected int aXS;
    protected float aQK;
    protected int cDu;
    protected boolean eum;
    protected int eun;
    protected boolean euo;
    protected int eup;
    protected int euq;
    protected boolean eur;
    protected int eus;
    protected fvd tyG;

    public int d() {
        return this.o;
    }

    public int AM() {
        return this.aXS;
    }

    public float aSL() {
        return this.aQK;
    }

    public int bBE() {
        return this.cDu;
    }

    public boolean cxW() {
        return this.eum;
    }

    public int cxX() {
        return this.eun;
    }

    public boolean cxY() {
        return this.euo;
    }

    public int cxZ() {
        return this.eup;
    }

    public int cya() {
        return this.euq;
    }

    public boolean cyb() {
        return this.eur;
    }

    public int cyc() {
        return this.eus;
    }

    public fvd gnz() {
        return this.tyG;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.aXS = 0;
        this.aQK = 0.0f;
        this.cDu = 0;
        this.eum = false;
        this.eun = 0;
        this.euo = false;
        this.eup = 0;
        this.euq = 0;
        this.eur = false;
        this.eus = 0;
        this.tyG = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.aXS = aqH2.bGI();
        this.aQK = aqH2.bGH();
        this.cDu = aqH2.bGI();
        this.eum = aqH2.bxv();
        this.eun = aqH2.bGI();
        this.euo = aqH2.bxv();
        this.eup = aqH2.bGI();
        this.euq = aqH2.bGI();
        this.eur = aqH2.bxv();
        this.eus = aqH2.bGI();
        if (aqH2.aTf() != 0) {
            this.tyG = new fvd();
            this.tyG.a(aqH2);
        } else {
            this.tyG = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozI.d();
    }
}
