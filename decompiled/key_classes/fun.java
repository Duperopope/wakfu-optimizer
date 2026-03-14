/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aqH
 *  aqz
 *  ewj
 *  fup
 *  fur
 */
public class fun
implements aqz {
    protected int o;
    protected int efP;
    protected boolean bYX;
    protected boolean dxk;
    protected String asF;
    protected String efR;
    protected fup[] tyo;
    protected fur[] typ;
    protected int bMn;
    protected int efU;
    protected boolean efV;
    protected boolean efW;
    protected boolean efX;
    protected int efY;
    protected boolean ega;
    protected int tyq;
    protected long[] tyr;
    protected long egc;
    protected long egd;
    protected boolean tys;
    protected boolean egz;
    protected boolean egf;
    protected int egg;
    protected byte egh;
    protected int egi;
    protected boolean tyt;

    public int d() {
        return this.o;
    }

    public int cjd() {
        return this.efP;
    }

    public boolean isVisible() {
        return this.bYX;
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

    public fup[] gni() {
        return this.tyo;
    }

    public fur[] gnj() {
        return this.typ;
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

    public boolean cjn() {
        return this.ega;
    }

    public int bMY() {
        return this.tyq;
    }

    public long[] gnk() {
        return this.tyr;
    }

    public long cjp() {
        return this.egc;
    }

    public long cjq() {
        return this.egd;
    }

    public boolean gnl() {
        return this.tys;
    }

    public boolean cjL() {
        return this.egz;
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

    public boolean gnm() {
        return this.tyt;
    }

    public void reset() {
        this.o = 0;
        this.efP = 0;
        this.bYX = false;
        this.dxk = false;
        this.asF = null;
        this.efR = null;
        this.tyo = null;
        this.typ = null;
        this.bMn = 0;
        this.efU = 0;
        this.efV = false;
        this.efW = false;
        this.efX = false;
        this.efY = 0;
        this.ega = false;
        this.tyq = 0;
        this.tyr = null;
        this.egc = 0L;
        this.egd = 0L;
        this.tys = false;
        this.egz = false;
        this.egf = false;
        this.egg = 0;
        this.egh = 0;
        this.egi = 0;
        this.tyt = false;
    }

    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.bYX = aqH2.bxv();
        this.dxk = aqH2.bxv();
        this.asF = aqH2.bGL().intern();
        this.efR = aqH2.bGL().intern();
        int n2 = aqH2.bGI();
        this.tyo = new fup[n2];
        for (n = 0; n < n2; ++n) {
            this.tyo[n] = new fup();
            this.tyo[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.typ = new fur[n];
        for (int i = 0; i < n; ++i) {
            this.typ[i] = new fur();
            this.typ[i].a(aqH2);
        }
        this.bMn = aqH2.bGI();
        this.efU = aqH2.bGI();
        this.efV = aqH2.bxv();
        this.efW = aqH2.bxv();
        this.efX = aqH2.bxv();
        this.efY = aqH2.bGI();
        this.ega = aqH2.bxv();
        this.tyq = aqH2.bGI();
        this.tyr = aqH2.bxz();
        this.egc = aqH2.bGK();
        this.egd = aqH2.bGK();
        this.tys = aqH2.bxv();
        this.egz = aqH2.bxv();
        this.egf = aqH2.bxv();
        this.egg = aqH2.bGI();
        this.egh = aqH2.aTf();
        this.egi = aqH2.bGI();
        this.tyt = aqH2.bxv();
    }

    public final int bGA() {
        return ewj.oyr.d();
    }
}
