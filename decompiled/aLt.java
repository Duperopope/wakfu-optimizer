/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLt
implements aqz {
    protected int eic;
    protected int eid;
    protected int eie;
    protected int eif;
    protected int ehO;
    protected int eig;
    protected byte eih;

    public int clt() {
        return this.eic;
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

    @Override
    public void reset() {
        this.eic = 0;
        this.eid = 0;
        this.eie = 0;
        this.eif = 0;
        this.ehO = 0;
        this.eig = 0;
        this.eih = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.eic = aqH2.bGI();
        this.eid = aqH2.bGI();
        this.eie = aqH2.bGI();
        this.eif = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.eig = aqH2.bGI();
        this.eih = aqH2.aTf();
    }

    @Override
    public final int bGA() {
        return ewj.oyy.d();
    }
}
