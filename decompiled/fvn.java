/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvn
implements aqz {
    protected int ejc;
    protected int ejd;
    protected float eje;
    protected boolean ejf;
    protected boolean ejg;
    protected boolean ejh;

    public int cms() {
        return this.ejc;
    }

    public int cmt() {
        return this.ejd;
    }

    public float cmu() {
        return this.eje;
    }

    public boolean cmv() {
        return this.ejf;
    }

    public boolean cmw() {
        return this.ejg;
    }

    public boolean cmx() {
        return this.ejh;
    }

    @Override
    public void reset() {
        this.ejc = 0;
        this.ejd = 0;
        this.eje = 0.0f;
        this.ejf = false;
        this.ejg = false;
        this.ejh = false;
    }

    @Override
    public void a(aqH aqH2) {
        this.ejc = aqH2.bGI();
        this.ejd = aqH2.bGI();
        this.eje = aqH2.bGH();
        this.ejf = aqH2.bxv();
        this.ejg = aqH2.bxv();
        this.ejh = aqH2.bxv();
    }

    @Override
    public final int bGA() {
        return ewj.oyN.d();
    }
}
