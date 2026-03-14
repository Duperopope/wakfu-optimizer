/*
 * Decompiled with CFR 0.152.
 */
public class fyo
implements aqz {
    protected String euA;
    protected int euB;
    protected int euC;
    protected int euD;

    public String cyk() {
        return this.euA;
    }

    public int cyl() {
        return this.euB;
    }

    public int cym() {
        return this.euC;
    }

    public int cyn() {
        return this.euD;
    }

    @Override
    public void reset() {
        this.euA = null;
        this.euB = 0;
        this.euC = 0;
        this.euD = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.euA = aqH2.bGL().intern();
        this.euB = aqH2.bGI();
        this.euC = aqH2.bGI();
        this.euD = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        throw new UnsupportedOperationException();
    }
}
