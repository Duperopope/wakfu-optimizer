/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aqz
 *  fxK
 *  fxL
 *  fxM
 */
public class fxJ
implements aqz {
    protected int o;
    protected int efP;
    protected long cwe;
    protected String eik;
    protected boolean eqG;
    protected int eoY;
    protected int[] baD;
    protected int eqH;
    protected int eqJ;
    protected boolean eqK;
    protected long eqL;
    protected long aZl;
    protected int eqM;
    protected fxK[] tBf;
    protected fxM[] tBg;
    protected fxL[] tBh;

    public int d() {
        return this.o;
    }

    public int cjd() {
        return this.efP;
    }

    public long Tz() {
        return this.cwe;
    }

    public String clB() {
        return this.eik;
    }

    public boolean cui() {
        return this.eqG;
    }

    public int tL() {
        return this.eoY;
    }

    public int[] ckm() {
        return this.baD;
    }

    public int cuj() {
        return this.eqH;
    }

    public int cul() {
        return this.eqJ;
    }

    public boolean cum() {
        return this.eqK;
    }

    public long cun() {
        return this.eqL;
    }

    public long pf() {
        return this.aZl;
    }

    public int cuo() {
        return this.eqM;
    }

    public fxK[] gpY() {
        return this.tBf;
    }

    public fxM[] gpZ() {
        return this.tBg;
    }

    public fxL[] gqa() {
        return this.tBh;
    }

    public void reset() {
        this.o = 0;
        this.efP = 0;
        this.cwe = 0L;
        this.eik = null;
        this.eqG = false;
        this.eoY = 0;
        this.baD = null;
        this.eqH = 0;
        this.eqJ = 0;
        this.eqK = false;
        this.eqL = 0L;
        this.aZl = 0L;
        this.eqM = 0;
        this.tBf = null;
        this.tBg = null;
        this.tBh = null;
    }

    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.cwe = aqH2.bGK();
        this.eik = aqH2.bGL().intern();
        this.eqG = aqH2.bxv();
        this.eoY = aqH2.bGI();
        this.baD = aqH2.bGM();
        this.eqH = aqH2.bGI();
        this.eqJ = aqH2.bGI();
        this.eqK = aqH2.bxv();
        this.eqL = aqH2.bGK();
        this.aZl = aqH2.bGK();
        this.eqM = aqH2.bGI();
        int n3 = aqH2.bGI();
        this.tBf = new fxK[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tBf[n2] = new fxK();
            this.tBf[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tBg = new fxM[n2];
        for (n = 0; n < n2; ++n) {
            this.tBg[n] = new fxM();
            this.tBg[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.tBh = new fxL[n];
        for (int i = 0; i < n; ++i) {
            this.tBh[i] = new fxL();
            this.tBh[i].a(aqH2);
        }
    }

    public final int bGA() {
        return ewj.ozw.d();
    }
}
