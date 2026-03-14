/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLu
implements aqz {
    protected int o;
    protected int eii;
    protected int eij;
    protected String eik;
    protected String eil;
    protected boolean eim;
    protected aOP ein;

    public int d() {
        return this.o;
    }

    public int clz() {
        return this.eii;
    }

    public int clA() {
        return this.eij;
    }

    public String clB() {
        return this.eik;
    }

    public String clC() {
        return this.eil;
    }

    public boolean clD() {
        return this.eim;
    }

    public aOP clE() {
        return this.ein;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eii = 0;
        this.eij = 0;
        this.eik = null;
        this.eil = null;
        this.eim = false;
        this.ein = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eii = aqH2.bGI();
        this.eij = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        this.eil = aqH2.bGL().intern();
        this.eim = aqH2.bxv();
        this.ein = new aOP();
        ((aOp)this.ein).a(aqH2);
    }

    @Override
    public final int bGA() {
        return ewj.oyz.d();
    }
}
