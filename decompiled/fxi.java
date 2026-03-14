/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fxi
implements aqz {
    protected int o;
    protected int epc;
    protected int ciZ;
    protected int epA;
    protected int epe;
    protected long eph;
    protected long epi;
    protected byte epg;
    protected short epf;
    protected short enc;
    protected fxl[] tAN;
    protected fxk[] tAO;
    protected fxm[] tAP;
    protected fxn[] tAQ;
    protected int[] epF;
    protected fxj[] tAR;

    public int d() {
        return this.o;
    }

    public int AK() {
        return this.epc;
    }

    public int aVt() {
        return this.ciZ;
    }

    public int ctd() {
        return this.epA;
    }

    public int agM() {
        return this.epe;
    }

    public long csJ() {
        return this.eph;
    }

    public long csK() {
        return this.epi;
    }

    public byte csI() {
        return this.epg;
    }

    public short csH() {
        return this.epf;
    }

    public short cqA() {
        return this.enc;
    }

    public fxl[] gpG() {
        return this.tAN;
    }

    public fxk[] gpH() {
        return this.tAO;
    }

    public fxm[] gpI() {
        return this.tAP;
    }

    public fxn[] gpJ() {
        return this.tAQ;
    }

    public int[] cti() {
        return this.epF;
    }

    public fxj[] gpK() {
        return this.tAR;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.epc = 0;
        this.ciZ = 0;
        this.epA = 0;
        this.epe = 0;
        this.eph = 0L;
        this.epi = 0L;
        this.epg = 0;
        this.epf = 0;
        this.enc = 0;
        this.tAN = null;
        this.tAO = null;
        this.tAP = null;
        this.tAQ = null;
        this.epF = null;
        this.tAR = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        int n3;
        int n4;
        this.o = aqH2.bGI();
        this.epc = aqH2.bGI();
        this.ciZ = aqH2.bGI();
        this.epA = aqH2.bGI();
        this.epe = aqH2.bGI();
        this.eph = aqH2.bGK();
        this.epi = aqH2.bGK();
        this.epg = aqH2.aTf();
        this.epf = aqH2.bGG();
        this.enc = aqH2.bGG();
        int n5 = aqH2.bGI();
        this.tAN = new fxl[n5];
        for (n4 = 0; n4 < n5; ++n4) {
            this.tAN[n4] = new fxl();
            this.tAN[n4].a(aqH2);
        }
        n4 = aqH2.bGI();
        this.tAO = new fxk[n4];
        for (n3 = 0; n3 < n4; ++n3) {
            this.tAO[n3] = new fxk();
            this.tAO[n3].a(aqH2);
        }
        n3 = aqH2.bGI();
        this.tAP = new fxm[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tAP[n2] = new fxm();
            this.tAP[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tAQ = new fxn[n2];
        for (n = 0; n < n2; ++n) {
            this.tAQ[n] = new fxn();
            ((fxN)this.tAQ[n]).a(aqH2);
        }
        this.epF = aqH2.bGM();
        n = aqH2.bGI();
        this.tAR = new fxj[n];
        for (int i = 0; i < n; ++i) {
            this.tAR[i] = new fxj();
            this.tAR[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAB.d();
    }
}
