/*
 * Decompiled with CFR 0.152.
 */
public class aMs {
    protected int o;
    protected String eik;
    protected float ekw;
    protected aMr[] ekx;

    public int d() {
        return this.o;
    }

    public String clB() {
        return this.eik;
    }

    public float cnK() {
        return this.ekw;
    }

    public aMr[] cnL() {
        return this.ekx;
    }

    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eik = aqH2.bGL().intern();
        this.ekw = aqH2.bGH();
        int n = aqH2.bGI();
        this.ekx = new aMr[n];
        for (int i = 0; i < n; ++i) {
            this.ekx[i] = new aMr();
            this.ekx[i].a(aqH2);
        }
    }
}
