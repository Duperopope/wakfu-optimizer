/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuX
implements aqz {
    protected int eiu;
    protected int ehO;
    protected int asA;
    protected int eiv;
    protected fuY[] tyT;

    public int clL() {
        return this.eiu;
    }

    public int clf() {
        return this.ehO;
    }

    public int azv() {
        return this.asA;
    }

    public int clM() {
        return this.eiv;
    }

    public fuY[] gnM() {
        return this.tyT;
    }

    @Override
    public void reset() {
        this.eiu = 0;
        this.ehO = 0;
        this.asA = 0;
        this.eiv = 0;
        this.tyT = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.eiu = aqH2.bGI();
        this.ehO = aqH2.bGI();
        this.asA = aqH2.bGI();
        this.eiv = aqH2.bGI();
        int n = aqH2.bGI();
        this.tyT = new fuY[n];
        for (int i = 0; i < n; ++i) {
            this.tyT[i] = new fuY();
            this.tyT[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyC.d();
    }
}
