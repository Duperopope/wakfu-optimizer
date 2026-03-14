/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLp
implements aqz {
    protected int o;
    protected int ehT;
    protected aLq[] ehU;
    protected aLr[] ehV;

    public int d() {
        return this.o;
    }

    public int clk() {
        return this.ehT;
    }

    public aLq[] cll() {
        return this.ehU;
    }

    public aLr[] clm() {
        return this.ehV;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehT = 0;
        this.ehU = null;
        this.ehV = null;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.ehT = aqH2.bGI();
        int n2 = aqH2.bGI();
        this.ehU = new aLq[n2];
        for (n = 0; n < n2; ++n) {
            this.ehU[n] = new aLq();
            ((aLQ)this.ehU[n]).a(aqH2);
        }
        n = aqH2.bGI();
        this.ehV = new aLr[n];
        for (int i = 0; i < n; ++i) {
            this.ehV[i] = new aLr();
            this.ehV[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAX.d();
    }
}
