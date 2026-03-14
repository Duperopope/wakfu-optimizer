/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOp
implements aqz {
    protected int o;
    protected int ehb;
    protected aLD ehd;

    public int d() {
        return this.o;
    }

    public int ckr() {
        return this.ehb;
    }

    public aLD ckt() {
        return this.ehd;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ehb = 0;
        this.ehd = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ehb = aqH2.bGI();
        if (aqH2.aTf() != 0) {
            this.ehd = new aLD();
            ((aLd)this.ehd).a(aqH2);
        } else {
            this.ehd = null;
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozW.d();
    }
}
