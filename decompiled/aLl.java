/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aLl
implements aqz {
    protected int o;
    protected short aXy;
    protected aLm[] ehL;

    public int d() {
        return this.o;
    }

    public short clb() {
        return this.aXy;
    }

    public aLm[] clc() {
        return this.ehL;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.aXy = 0;
        this.ehL = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.aXy = aqH2.bGG();
        int n = aqH2.bGI();
        this.ehL = new aLm[n];
        for (int i = 0; i < n; ++i) {
            this.ehL[i] = new aLm();
            ((aLM)this.ehL[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyw.d();
    }
}
