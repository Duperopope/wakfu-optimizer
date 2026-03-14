/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aOm
 *  aOn
 *  aOo
 *  aqz
 */
public class aOl
implements aqz {
    protected int o;
    protected int efP;
    protected long cwe;
    protected String eik;
    protected String eqF;
    protected boolean eqG;
    protected int eoY;
    protected int[] baD;
    protected int eqH;
    protected int[] eqI;
    protected int eqJ;
    protected boolean eqK;
    protected long eqL;
    protected long aZl;
    protected int eqM;
    protected aOm[] eqN;
    protected aOo[] eqO;
    protected aOn[] eqP;

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

    public String cuh() {
        return this.eqF;
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

    public int[] cuk() {
        return this.eqI;
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

    public aOm[] cup() {
        return this.eqN;
    }

    public aOo[] cuq() {
        return this.eqO;
    }

    public aOn[] cur() {
        return this.eqP;
    }

    public void reset() {
        this.o = 0;
        this.efP = 0;
        this.cwe = 0L;
        this.eik = null;
        this.eqF = null;
        this.eqG = false;
        this.eoY = 0;
        this.baD = null;
        this.eqH = 0;
        this.eqI = null;
        this.eqJ = 0;
        this.eqK = false;
        this.eqL = 0L;
        this.aZl = 0L;
        this.eqM = 0;
        this.eqN = null;
        this.eqO = null;
        this.eqP = null;
    }

    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.cwe = aqH2.bGK();
        this.eik = aqH2.bGL().intern();
        this.eqF = aqH2.bGL().intern();
        this.eqG = aqH2.bxv();
        this.eoY = aqH2.bGI();
        this.baD = aqH2.bGM();
        this.eqH = aqH2.bGI();
        this.eqI = aqH2.bGM();
        this.eqJ = aqH2.bGI();
        this.eqK = aqH2.bxv();
        this.eqL = aqH2.bGK();
        this.aZl = aqH2.bGK();
        this.eqM = aqH2.bGI();
        int n3 = aqH2.bGI();
        this.eqN = new aOm[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.eqN[n2] = new aOm();
            this.eqN[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.eqO = new aOo[n2];
        for (n = 0; n < n2; ++n) {
            this.eqO[n] = new aOo();
            this.eqO[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.eqP = new aOn[n];
        for (int i = 0; i < n; ++i) {
            this.eqP[i] = new aOn();
            this.eqP[i].a(aqH2);
        }
    }

    public final int bGA() {
        return ewj.ozw.d();
    }
}
