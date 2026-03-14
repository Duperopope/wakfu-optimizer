/*
 * Decompiled with CFR 0.152.
 */
public class aMx {
    protected int ekI;
    protected short ekJ;
    protected String ekK;
    protected String ekL;
    protected boolean ekM;
    protected aMy[] ekN;

    public int cnV() {
        return this.ekI;
    }

    public short cnW() {
        return this.ekJ;
    }

    public String cnX() {
        return this.ekK;
    }

    public String cnY() {
        return this.ekL;
    }

    public boolean cnZ() {
        return this.ekM;
    }

    public aMy[] coa() {
        return this.ekN;
    }

    public void a(aqH aqH2) {
        this.ekI = aqH2.bGI();
        this.ekJ = aqH2.bGG();
        this.ekK = aqH2.bGL().intern();
        this.ekL = aqH2.bGL().intern();
        this.ekM = aqH2.bxv();
        int n = aqH2.bGI();
        this.ekN = new aMy[n];
        for (int i = 0; i < n; ++i) {
            this.ekN[i] = new aMy();
            this.ekN[i].a(aqH2);
        }
    }
}
