/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aNj
implements aqz {
    protected int o;
    protected int ehO;
    protected int efU;
    protected int emS;
    protected int emT;
    protected int emU;
    protected boolean ekA;
    protected int emV;
    protected boolean emW;
    protected int ekB;
    protected String eik;
    protected aLD ehd;

    public int d() {
        return this.o;
    }

    public int clf() {
        return this.ehO;
    }

    public int cji() {
        return this.efU;
    }

    public int cqq() {
        return this.emS;
    }

    public int cqr() {
        return this.emT;
    }

    public int cqs() {
        return this.emU;
    }

    public boolean cnO() {
        return this.ekA;
    }

    public int cqt() {
        return this.emV;
    }

    public boolean cqu() {
        return this.emW;
    }

    public int cnP() {
        return this.ekB;
    }

    public String clB() {
        return this.eik;
    }

    public aLD ckt() {
        return this.ehd;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehO = 0;
        this.efU = 0;
        this.emS = 0;
        this.emT = 0;
        this.emU = 0;
        this.ekA = false;
        this.emV = 0;
        this.emW = false;
        this.ekB = 0;
        this.eik = null;
        this.ehd = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.efU = aqH2.bGI();
        this.emS = aqH2.bGI();
        this.emT = aqH2.bGI();
        this.emU = aqH2.bGI();
        this.ekA = aqH2.bxv();
        this.emV = aqH2.bGI();
        this.emW = aqH2.bxv();
        this.ekB = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        if (aqH2.aTf() != 0) {
            this.ehd = new aLD();
            ((aLd)this.ehd).a(aqH2);
        } else {
            this.ehd = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozc.d();
    }
}
