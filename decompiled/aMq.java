/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aMq
implements aqz {
    protected int o;
    protected aMt[] ekt;
    protected aLD ehd;

    public int d() {
        return this.o;
    }

    public aMt[] cnH() {
        return this.ekt;
    }

    public aLD ckt() {
        return this.ehd;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ekt = null;
        this.ehd = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        int n = aqH2.bGI();
        this.ekt = new aMt[n];
        for (int i = 0; i < n; ++i) {
            this.ekt[i] = new aMt();
            ((aMT)this.ekt[i]).a(aqH2);
        }
        if (aqH2.aTf() != 0) {
            this.ehd = new aLD();
            ((aLd)this.ehd).a(aqH2);
        } else {
            this.ehd = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.oyV.d();
    }
}
