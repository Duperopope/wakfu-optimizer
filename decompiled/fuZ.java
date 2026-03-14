/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuZ
implements aqz {
    protected int o;
    protected boolean bKS;
    protected int eiy;
    protected int eiz;
    protected String bKP;

    public int d() {
        return this.o;
    }

    public boolean bkX() {
        return this.bKS;
    }

    public int clP() {
        return this.eiy;
    }

    public int clQ() {
        return this.eiz;
    }

    public String getText() {
        return this.bKP;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.bKS = false;
        this.eiy = 0;
        this.eiz = 0;
        this.bKP = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.bKS = aqH2.bxv();
        this.eiy = aqH2.bGI();
        this.eiz = aqH2.bGI();
        this.bKP = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.oyD.d();
    }
}
