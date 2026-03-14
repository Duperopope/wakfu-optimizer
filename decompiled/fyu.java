/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fyu
implements aqz {
    protected int euR;
    protected int eid;
    protected int eie;
    protected int eif;
    protected int ehO;
    protected boolean euS;
    protected String euT;
    protected fyo tyP;

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

    public boolean cyC() {
        return this.euS;
    }

    public String cyD() {
        return this.euT;
    }

    public fyo gnI() {
        return this.tyP;
    }

    @Override
    public void reset() {
        this.euR = 0;
        this.eid = 0;
        this.eie = 0;
        this.eif = 0;
        this.ehO = 0;
        this.euS = false;
        this.euT = null;
        this.tyP = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.euR = aqH2.bGI();
        this.eid = aqH2.bGI();
        this.eie = aqH2.bGI();
        this.eif = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.euS = aqH2.bxv();
        this.euT = aqH2.bGL().intern();
        if (aqH2.aTf() != 0) {
            this.tyP = new fyo();
            this.tyP.a(aqH2);
        } else {
            this.tyP = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozN.d();
    }
}
