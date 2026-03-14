/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLY
implements aqz {
    protected int o;
    protected int ehO;
    protected boolean ejv;
    protected int ejw;
    protected int ejx;
    protected String asF;

    public int d() {
        return this.o;
    }

    public int clf() {
        return this.ehO;
    }

    public boolean cmN() {
        return this.ejv;
    }

    public int cmO() {
        return this.ejw;
    }

    public int cmP() {
        return this.ejx;
    }

    public String aGr() {
        return this.asF;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehO = 0;
        this.ejv = false;
        this.ejw = 0;
        this.ejx = 0;
        this.asF = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.ejv = aqH2.bxv();
        this.ejw = aqH2.bGI();
        this.ejx = aqH2.bGI();
        this.asF = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.oAC.d();
    }
}
