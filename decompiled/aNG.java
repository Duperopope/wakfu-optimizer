/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aNG
implements aqz {
    protected int o;
    protected String eiI;

    public int d() {
        return this.o;
    }

    public String ajo() {
        return this.eiI;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eiI = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eiI = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.ozp.d();
    }
}
