/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fyd
implements aqz {
    protected int o;
    protected int ehO;
    protected boolean etV;
    protected String etW;
    protected fyf[] tBq;
    protected fyf[] tBr;
    protected fye[] tBs;
    protected fyg[] tBt;
    protected fyh[] tBu;

    public int d() {
        return this.o;
    }

    public int clf() {
        return this.ehO;
    }

    public boolean cxF() {
        return this.etV;
    }

    public String cxG() {
        return this.etW;
    }

    public fyf[] gqj() {
        return this.tBq;
    }

    public fyf[] gqk() {
        return this.tBr;
    }

    public fye[] gql() {
        return this.tBs;
    }

    public fyg[] gqm() {
        return this.tBt;
    }

    public fyh[] gqn() {
        return this.tBu;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehO = 0;
        this.etV = false;
        this.etW = null;
        this.tBq = null;
        this.tBr = null;
        this.tBs = null;
        this.tBt = null;
        this.tBu = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        int n3;
        int n4;
        this.o = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.etV = aqH2.bxv();
        this.etW = aqH2.bGL().intern();
        int n5 = aqH2.bGI();
        this.tBq = new fyf[n5];
        for (n4 = 0; n4 < n5; ++n4) {
            this.tBq[n4] = new fyf();
            this.tBq[n4].a(aqH2);
        }
        n4 = aqH2.bGI();
        this.tBr = new fyf[n4];
        for (n3 = 0; n3 < n4; ++n3) {
            this.tBr[n3] = new fyf();
            this.tBr[n3].a(aqH2);
        }
        n3 = aqH2.bGI();
        this.tBs = new fye[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tBs[n2] = new fye();
            this.tBs[n2].a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tBt = new fyg[n2];
        for (n = 0; n < n2; ++n) {
            this.tBt[n] = new fyg();
            this.tBt[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.tBu = new fyh[n];
        for (int i = 0; i < n; ++i) {
            this.tBu[i] = new fyh();
            this.tBu[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBi.d();
    }
}
