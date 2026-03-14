/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOV
implements aqz {
    protected int euR;
    protected int eid;
    protected int eie;
    protected int eif;
    protected int ehO;
    protected int eig;
    protected byte eih;
    protected boolean euS;
    protected String euT;
    protected int cxt;
    protected int efP;
    protected aOP ein;

    public int cyB() {
        return this.euR;
    }

    public int clu() {
        return this.eid;
    }

    public int clv() {
        return this.eie;
    }

    public int clw() {
        return this.eif;
    }

    public int clf() {
        return this.ehO;
    }

    public int clx() {
        return this.eig;
    }

    public byte cly() {
        return this.eih;
    }

    public boolean cyC() {
        return this.euS;
    }

    public String cyD() {
        return this.euT;
    }

    public int wp() {
        return this.cxt;
    }

    public int cjd() {
        return this.efP;
    }

    public aOP clE() {
        return this.ein;
    }

    @Override
    public void reset() {
        this.euR = 0;
        this.eid = 0;
        this.eie = 0;
        this.eif = 0;
        this.ehO = 0;
        this.eig = 0;
        this.eih = 0;
        this.euS = false;
        this.euT = null;
        this.cxt = 0;
        this.efP = 0;
        this.ein = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.euR = aqH2.bGI();
        this.eid = aqH2.bGI();
        this.eie = aqH2.bGI();
        this.eif = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.eig = aqH2.bGI();
        this.eih = aqH2.aTf();
        this.euS = aqH2.bxv();
        this.euT = aqH2.bGL().intern();
        this.cxt = aqH2.bGI();
        this.efP = aqH2.bGI();
        if (aqH2.aTf() != 0) {
            this.ein = new aOP();
            ((aOp)this.ein).a(aqH2);
        } else {
            this.ein = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozN.d();
    }
}
