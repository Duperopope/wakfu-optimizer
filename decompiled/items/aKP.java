/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aKQ
 *  aKS
 *  aqH
 *  aqz
 *  ewj
 */
public class aKP
implements aqz {
    protected int o;
    protected int efP;
    protected boolean bYX;
    protected boolean efQ;
    protected boolean dxk;
    protected String asF;
    protected String efR;
    protected aKQ[] efS;
    protected aKS[] efT;
    protected int bMn;
    protected int efU;
    protected boolean efV;
    protected boolean efW;
    protected boolean efX;
    protected int efY;
    protected int efZ;
    protected boolean ega;
    protected int egb;
    protected long egc;
    protected long egd;
    protected boolean ege;
    protected int ciZ;
    protected boolean egf;
    protected int egg;
    protected byte egh;
    protected int egi;
    protected String egj;
    protected int bIi;

    public int d() {
        return this.o;
    }

    public int cjd() {
        return this.efP;
    }

    public boolean isVisible() {
        return this.bYX;
    }

    public boolean cje() {
        return this.efQ;
    }

    public boolean apo() {
        return this.dxk;
    }

    public String aGr() {
        return this.asF;
    }

    public String cjf() {
        return this.efR;
    }

    public aKQ[] cjg() {
        return this.efS;
    }

    public aKS[] cjh() {
        return this.efT;
    }

    public int getDuration() {
        return this.bMn;
    }

    public int cji() {
        return this.efU;
    }

    public boolean cjj() {
        return this.efV;
    }

    public boolean aYo() {
        return this.efW;
    }

    public boolean cjk() {
        return this.efX;
    }

    public int cjl() {
        return this.efY;
    }

    public int cjm() {
        return this.efZ;
    }

    public boolean cjn() {
        return this.ega;
    }

    public int cjo() {
        return this.egb;
    }

    public long cjp() {
        return this.egc;
    }

    public long cjq() {
        return this.egd;
    }

    public boolean cjr() {
        return this.ege;
    }

    public int aVt() {
        return this.ciZ;
    }

    public boolean cjs() {
        return this.egf;
    }

    public int cjt() {
        return this.egg;
    }

    public byte cju() {
        return this.egh;
    }

    public int aYs() {
        return this.egi;
    }

    public String cjv() {
        return this.egj;
    }

    public int aeV() {
        return this.bIi;
    }

    public void reset() {
        this.o = 0;
        this.efP = 0;
        this.bYX = false;
        this.efQ = false;
        this.dxk = false;
        this.asF = null;
        this.efR = null;
        this.efS = null;
        this.efT = null;
        this.bMn = 0;
        this.efU = 0;
        this.efV = false;
        this.efW = false;
        this.efX = false;
        this.efY = 0;
        this.efZ = 0;
        this.ega = false;
        this.egb = 0;
        this.egc = 0L;
        this.egd = 0L;
        this.ege = false;
        this.ciZ = 0;
        this.egf = false;
        this.egg = 0;
        this.egh = 0;
        this.egi = 0;
        this.egj = null;
        this.bIi = 0;
    }

    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.bYX = aqH2.bxv();
        this.efQ = aqH2.bxv();
        this.dxk = aqH2.bxv();
        this.asF = aqH2.bGL().intern();
        this.efR = aqH2.bGL().intern();
        int n2 = aqH2.bGI();
        this.efS = new aKQ[n2];
        for (n = 0; n < n2; ++n) {
            this.efS[n] = new aKQ();
            this.efS[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.efT = new aKS[n];
        for (int i = 0; i < n; ++i) {
            this.efT[i] = new aKS();
            this.efT[i].a(aqH2);
        }
        this.bMn = aqH2.bGI();
        this.efU = aqH2.bGI();
        this.efV = aqH2.bxv();
        this.efW = aqH2.bxv();
        this.efX = aqH2.bxv();
        this.efY = aqH2.bGI();
        this.efZ = aqH2.bGI();
        this.ega = aqH2.bxv();
        this.egb = aqH2.bGI();
        this.egc = aqH2.bGK();
        this.egd = aqH2.bGK();
        this.ege = aqH2.bxv();
        this.ciZ = aqH2.bGI();
        this.egf = aqH2.bxv();
        this.egg = aqH2.bGI();
        this.egh = aqH2.aTf();
        this.egi = aqH2.bGI();
        this.egj = aqH2.bGL().intern();
        this.bIi = aqH2.bGI();
    }

    public final int bGA() {
        return ewj.oyr.d();
    }
}
