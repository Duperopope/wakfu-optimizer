/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvh
implements aqz {
    protected int eiQ;
    protected String eik;
    protected int bMn;
    protected short bMo;
    protected float eiR;
    protected float eiS;

    public int cmh() {
        return this.eiQ;
    }

    public String clB() {
        return this.eik;
    }

    public int getDuration() {
        return this.bMn;
    }

    public short blw() {
        return this.bMo;
    }

    public float cmi() {
        return this.eiR;
    }

    public float cmj() {
        return this.eiS;
    }

    @Override
    public void reset() {
        this.eiQ = 0;
        this.eik = null;
        this.bMn = 0;
        this.bMo = 0;
        this.eiR = 0.0f;
        this.eiS = 0.0f;
    }

    @Override
    public void a(aqH aqH2) {
        this.eiQ = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        this.bMn = aqH2.bGI();
        this.bMo = aqH2.bGG();
        this.eiR = aqH2.bGH();
        this.eiS = aqH2.bGH();
    }

    @Override
    public final int bGA() {
        return ewj.oyK.d();
    }
}
