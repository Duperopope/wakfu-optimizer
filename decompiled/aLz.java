/*
 * Decompiled with CFR 0.152.
 */
public class aLz {
    protected int o;
    protected int eid;
    protected int eie;
    protected int eif;
    protected int eix;
    protected String eik;
    protected aOP ein;

    public int d() {
        return this.o;
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

    public int clO() {
        return this.eix;
    }

    public String clB() {
        return this.eik;
    }

    public aOP clE() {
        return this.ein;
    }

    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eid = aqH2.bGI();
        this.eie = aqH2.bGI();
        this.eif = aqH2.bGI();
        this.eix = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        if (aqH2.aTf() != 0) {
            this.ein = new aOP();
            ((aOp)this.ein).a(aqH2);
        } else {
            this.ein = null;
        }
    }
}
