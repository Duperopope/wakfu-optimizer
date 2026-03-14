/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aMT
 *  aqH
 *  aqz
 *  ewj
 */
import java.util.HashMap;

public class aMS
implements aqz {
    protected int o;
    protected short elD;
    protected short aXk;
    protected int bap;
    protected int baq;
    protected short ban;
    protected short bat;
    protected boolean bau;
    protected boolean bav;
    protected boolean baw;
    protected boolean bax;
    protected byte bay;
    protected short baz;
    protected String baB;
    protected int baC;
    protected int[] baD;
    protected aMT[] elE;
    protected HashMap<Short, Integer> elF;
    protected int[] cjr;

    public int d() {
        return this.o;
    }

    public short coV() {
        return this.elD;
    }

    public short bdL() {
        return this.aXk;
    }

    public int getX() {
        return this.bap;
    }

    public int getY() {
        return this.baq;
    }

    public short bdi() {
        return this.ban;
    }

    public short coW() {
        return this.bat;
    }

    public boolean coX() {
        return this.bau;
    }

    public boolean coY() {
        return this.bav;
    }

    public boolean bcS() {
        return this.baw;
    }

    public boolean coZ() {
        return this.bax;
    }

    public byte coI() {
        return this.bay;
    }

    public short bei() {
        return this.baz;
    }

    public String cpa() {
        return this.baB;
    }

    public int cor() {
        return this.baC;
    }

    public int[] ckm() {
        return this.baD;
    }

    public aMT[] cpb() {
        return this.elE;
    }

    public HashMap<Short, Integer> cpc() {
        return this.elF;
    }

    public int[] cpd() {
        return this.cjr;
    }

    public void reset() {
        this.o = 0;
        this.elD = 0;
        this.aXk = 0;
        this.bap = 0;
        this.baq = 0;
        this.ban = 0;
        this.bat = 0;
        this.bau = false;
        this.bav = false;
        this.baw = false;
        this.bax = false;
        this.bay = 0;
        this.baz = 0;
        this.baB = null;
        this.baC = 0;
        this.baD = null;
        this.elE = null;
        this.elF = null;
        this.cjr = null;
    }

    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.elD = aqH2.bGG();
        this.aXk = aqH2.bGG();
        this.bap = aqH2.bGI();
        this.baq = aqH2.bGI();
        this.ban = aqH2.bGG();
        this.bat = aqH2.bGG();
        this.bau = aqH2.bxv();
        this.bav = aqH2.bxv();
        this.baw = aqH2.bxv();
        this.bax = aqH2.bxv();
        this.bay = aqH2.aTf();
        this.baz = aqH2.bGG();
        this.baB = aqH2.bGL().intern();
        this.baC = aqH2.bGI();
        this.baD = aqH2.bGM();
        int n2 = aqH2.bGI();
        this.elE = new aMT[n2];
        for (n = 0; n < n2; ++n) {
            this.elE[n] = new aMT();
            this.elE[n].a(aqH2);
        }
        n = aqH2.bGI();
        this.elF = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            short s = aqH2.bGG();
            int n3 = aqH2.bGI();
            this.elF.put(s, n3);
        }
        this.cjr = aqH2.bGM();
    }

    public final int bGA() {
        return ewj.oAL.d();
    }
}
